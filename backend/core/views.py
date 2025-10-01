import os
from rest_framework import permissions, status, viewsets, serializers
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.response import Response

from rest_framework.decorators import action
from .search import index_document, get_client as get_search_client
from .models import (
    AgendaItem,
    Committee,
    Document,
    Lead,
    Meeting,
    Motion,
    OParlSource,
    Organization,
    Person,
    RoleAssignment,
    ShareLink,
    Team,
    TeamMembership,
    Tenant,
    PasswordResetToken,
    Subspace,
    SpaceMembership,
    Plan,
    Subscription,
    UsageMeter,
    FeatureFlag,
    Note,
    WorkflowConfig,
    AuditLog,
    WebhookEndpoint,
    ApiKey,
    PricingAgreement,
    Membership,
    Invitation,
    StaffProfile,
    OfferDraft,
)
from .serializers import (
	AgendaItemSerializer,
	CommitteeSerializer,
	DocumentSerializer,
	LeadSerializer,
	MeetingSerializer,
	MotionSerializer,
    OParlSourceSerializer,
	OrganizationSerializer,
	PersonSerializer,
	RoleAssignmentSerializer,
	PasswordResetRequestSerializer,
	PasswordResetConfirmSerializer,
	ShareLinkSerializer,
    TeamMembershipSerializer,
    TeamSerializer,
	TenantSerializer,
    SubspaceSerializer,
    SpaceMembershipSerializer,
    PlanSerializer,
    SubscriptionSerializer,
    UsageMeterSerializer,
    FeatureFlagSerializer,
    NoteSerializer,
    WorkflowConfigSerializer,
    AuditLogSerializer,
    WebhookEndpointSerializer,
    ApiKeySerializer,
    OAuthClientSerializer,
    PricingAgreementSerializer,
    MembershipSerializer,
    InvitationSerializer,
    StaffProfileSerializer,
    OfferDraftSerializer,
    RoleSerializer,
    UserRoleSerializer,
)


class BaseTenantViewSet(viewsets.ModelViewSet):
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]

	def get_queryset(self):
		qs = super().get_queryset()
		tenant_id = self.request.query_params.get("tenant")
		if tenant_id:
			qs = qs.filter(tenant_id=tenant_id)
		return qs


class TenantViewSet(viewsets.ModelViewSet):
	queryset = Tenant.objects.all()
	serializer_class = TenantSerializer
	permission_classes = [permissions.IsAdminUser]

	@action(detail=True, methods=["post"], url_path="create-subspace")
	def create_subspace(self, request, pk=None):
		"""Platzhalter: Subspace/Domain-Provisionierung triggern."""
		tenant = self.get_object()
		# Hier könnten DNS/Ingress/Storage-Routinen angestoßen werden.
		return Response({"detail": f"Subspace für {tenant.slug} angestoßen."})

	@action(detail=True, methods=["post"], url_path="deactivate")
	def deactivate(self, request, pk=None):
		tenant = self.get_object()
		tenant.is_active = False
		tenant.save(update_fields=["is_active"])
		return Response({"detail": "Deaktiviert"})

	@action(detail=True, methods=["post"], url_path="reactivate")
	def reactivate(self, request, pk=None):
		tenant = self.get_object()
		tenant.is_active = True
		tenant.save(update_fields=["is_active"])
		return Response({"detail": "Reaktiviert"})

	@action(detail=False, methods=["get"], url_path="branding", permission_classes=[permissions.AllowAny])
	def branding(self, request):
		# Offen zugänglich: Branding darf vor Login geladen werden
		# Ermittelt Tenant anhand von Host oder Header und gibt Branding zurück
		host = request.get_host().split(":")[0]
		slug_or_domain = request.headers.get("X-Tenant") or request.query_params.get("tenant") or host
		tenant = Tenant.objects.filter(domain=slug_or_domain).first() or Tenant.objects.filter(slug=slug_or_domain).first()
		if not tenant:
			return Response({
				"logo_url": "",
				"color_primary": "#0a75ff",
				"color_secondary": "#0f172a",
			})
		return Response({
			"id": tenant.id,
			"name": tenant.name,
			"slug": tenant.slug,
			"logo_url": tenant.logo_url,
			"color_primary": tenant.color_primary,
			"color_secondary": tenant.color_secondary,
		})


class CommitteeViewSet(BaseTenantViewSet):
	queryset = Committee.objects.all()
	serializer_class = CommitteeSerializer


class AdminMfaRequired(permissions.BasePermission):
	"""Erzwingt MFA für Admin-Endpunkte, wenn die Policy auf dem Tenant aktiv ist."""

	def has_permission(self, request, view):
		user = getattr(request, "user", None)
		if not user or not user.is_authenticated:
			return False
		path = getattr(request, "path", "") or ""
		if "/api/admin/" in path:
			tenant = getattr(user, "tenant", None)
			if tenant and getattr(tenant, "mfa_required_for_admins", False):
				if not getattr(user, "mfa_enabled", False):
					return False
		return True


class PersonViewSet(BaseTenantViewSet):
	queryset = Person.objects.all()
	serializer_class = PersonSerializer


class OrganizationViewSet(BaseTenantViewSet):
	queryset = Organization.objects.all()
	serializer_class = OrganizationSerializer


class MeetingViewSet(BaseTenantViewSet):
	queryset = Meeting.objects.all().select_related("committee")
	serializer_class = MeetingSerializer

	@action(detail=False, methods=["get"], url_path="my-agenda", permission_classes=[permissions.IsAuthenticated])
	def my_agenda(self, request):
		"""Sitzungen für Gremien, in denen der User Rollen hat."""
		user = request.user
		committee_ids = list(RoleAssignment.objects.filter(user=user).values_list("committee_id", flat=True))
		qs = self.get_queryset().filter(committee_id__in=committee_ids).order_by("start")
		ser = self.get_serializer(qs[:100], many=True)
		return Response(ser.data)


class AgendaItemViewSet(BaseTenantViewSet):
	queryset = AgendaItem.objects.all().select_related("meeting")
	serializer_class = AgendaItemSerializer


class DocumentViewSet(BaseTenantViewSet):
	queryset = Document.objects.all().select_related("agenda_item")
	serializer_class = DocumentSerializer

	def create(self, request, *args, **kwargs):
		content_hash = request.data.get("content_hash")
		tenant_id = request.data.get("tenant")
		if content_hash and tenant_id:
			existing = Document.objects.filter(tenant_id=tenant_id, content_hash=content_hash).first()
			if existing:
				ser = self.get_serializer(existing)
				return Response(ser.data, status=status.HTTP_200_OK)
		return super().create(request, *args, **kwargs)


	def list(self, request, *args, **kwargs):
		"""Einheitliche List-Parameter: q, filters[...], sort, page[size], page[after]."""
		qs = self.get_queryset()
		q = request.query_params.get("q", "").strip()
		if q:
			from django.db.models import Q
			qs = qs.filter(Q(title__icontains=q) | Q(content_text__icontains=q))
		for key, value in request.query_params.items():
			if key.startswith("filters[") and key.endswith("]"):
				field = key[8:-1]
				if value:
					qs = qs.filter(**{field: value})
		sort = request.query_params.get("sort")
		if sort:
			fields = [f.strip() for f in sort.split(",") if f.strip()]
			qs = qs.order_by(*fields)
		else:
			qs = qs.order_by("-created_at")
		after = request.query_params.get("page[after]")
		if after:
			try:
				after_id = int(after)
				qs = qs.filter(id__lt=after_id)
			except Exception:
				pass
		size = request.query_params.get("page[size]")
		limit = 50
		try:
			if size:
				limit = max(1, min(200, int(size)))
		except Exception:
			pass
		items = list(qs[:limit])
		ser = self.get_serializer(items, many=True)
		return Response({
			"data": ser.data,
			"next": items[-1].id if items else None,
		})


class MotionViewSet(BaseTenantViewSet):
	queryset = Motion.objects.all().select_related("author")
	serializer_class = MotionSerializer


class ShareLinkViewSet(viewsets.ModelViewSet):
	queryset = ShareLink.objects.all().select_related("motion")
	serializer_class = ShareLinkSerializer
	permission_classes = [permissions.AllowAny]


class SearchViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"], url_path="query")
    def query(self, request):
        """OpenSearch-DSL passthrough (Whitelist) mit Org-Scope."""
        client = get_search_client()
        body = request.data or {}
        allowed = {"query", "aggs", "sort", "from", "size", "suggest"}
        filtered = {k: v for k, v in body.items() if k in allowed}
        tenant_id = getattr(getattr(request, "user", None), "tenant_id", None)
        if tenant_id:
            scope_filter = {"term": {"tenant_id": tenant_id}}
            q = filtered.get("query") or {"match_all": {}}
            filtered["query"] = {"bool": {"must": [q], "filter": [scope_filter]}}
        index_name = os.getenv("OPENSEARCH_INDEX", "mandari-documents")
        try:
            res = client.search(index=index_name, body=filtered)
            return Response(res)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=["get"], url_path="suggest")
    def suggest(self, request):
        client = get_search_client()
        q = request.query_params.get("q", "")
        if not q:
            return Response({"suggest": []})
        index_name = os.getenv("OPENSEARCH_INDEX", "mandari-documents")
        body = {
            "suggest": {
                "title-term": {"text": q, "term": {"field": "title"}},
                "content-term": {"text": q, "term": {"field": "content_text"}},
            }
        }
        try:
            res = client.search(index=index_name, body=body)
            return Response(res.get("suggest", {}))
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class AiViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _call_ai(self, path: str, json: dict):
        import httpx
        base = os.getenv("AI_BASE_URL", "http://ai:8002")
        with httpx.Client(timeout=30.0) as client:
            r = client.post(f"{base}{path}", json=json)
            return r.status_code, r.json()

    @action(detail=False, methods=["post"], url_path="summarize")
    def summarize(self, request):
        text = request.data.get("text") or ""
        max_words = int(request.data.get("length", 120))
        status_code, data = self._call_ai("/summary", {"text": text, "max_words": max_words})
        try:
            AuditLog.objects.create(org=getattr(request.user, "tenant", None), actor=request.user if request.user.is_authenticated else None, action="ai.summarize", target_type="text", target_id="", diff_json={"len": len(text)})
        except Exception:
            pass
        return Response(data, status=status_code)

    @action(detail=False, methods=["post"], url_path="compare")
    def compare(self, request):
        return Response({"detail": "Not implemented in AI service"}, status=501)

    @action(detail=False, methods=["post"], url_path="gapcheck")
    def gapcheck(self, request):
        return Response({"detail": "Not implemented in AI service"}, status=501)

    @action(detail=False, methods=["post"], url_path="redact")
    def redact(self, request):
        return Response({"detail": "Not implemented in AI service"}, status=501)


class TeamViewSet(BaseTenantViewSet):
	queryset = Team.objects.all()
	serializer_class = TeamSerializer


class TeamMembershipViewSet(viewsets.ModelViewSet):
	queryset = TeamMembership.objects.all().select_related("team", "user")
	serializer_class = TeamMembershipSerializer


class OParlSourceViewSet(BaseTenantViewSet):
	queryset = OParlSource.objects.all()
	serializer_class = OParlSourceSerializer

	@action(detail=True, methods=["post"], url_path="trigger")
	def trigger(self, request, pk=None):
		# call ingest service
		try:
			import httpx
			source = self.get_object()
			base = os.getenv("INGEST_BASE_URL", "http://ingest:8001")
			with httpx.Client(timeout=30.0) as client:
				params = {"root": source.root_url, "tenant_id": source.tenant_id}
				if source.etag:
					params["etag"] = source.etag
				if source.last_modified:
					params["last_modified"] = source.last_modified
				r = client.post(f"{base}/oparl/ingest", params=params)
				data = r.json()
				# Aktualisiere ETag/Last-Modified
				if isinstance(data, dict):
					etag = data.get("etag")
					lm = data.get("last_modified")
					update_fields = []
					if etag and etag != source.etag:
						source.etag = etag
						update_fields.append("etag")
					if lm and lm != source.last_modified:
						source.last_modified = lm
						update_fields.append("last_modified")
					if update_fields:
						source.save(update_fields=update_fields)
				return Response(data, status=r.status_code)
		except Exception as e:
			return Response({"error": str(e)}, status=500)

	@action(detail=False, methods=["post"], url_path="validate")
	def validate(self, request):
		"""Validiert eine OParl-Quelle, ohne sie zu speichern."""
		root_url = request.data.get("root_url")
		if not root_url:
			return Response({"detail": "root_url erforderlich"}, status=400)
		try:
			import httpx
			with httpx.Client(timeout=10.0) as client:
				r = client.get(root_url)
				r.raise_for_status()
				j = r.json()
				ok = bool(j.get("body") or j.get("meeting") or j.get("paper"))
				return Response({"ok": ok, "keys": list(j.keys())[:20]})
		except Exception as e:
			return Response({"ok": False, "error": str(e)}, status=400)

	@action(detail=False, methods=["post"], url_path="create")
	def create_source(self, request):
		"""Alias für POST /connectors/oparl: Quelle anlegen & optional validieren."""
		validate_only = bool(request.data.get("validate_only"))
		if validate_only:
			return self.validate(request)
		ser = self.get_serializer(data=request.data)
		ser.is_valid(raise_exception=True)
		obj = ser.save()
		return Response(self.get_serializer(obj).data, status=201)


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by("-created_at")
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        # Erstellen und Bestätigen sind öffentlich (Website-Formular & Double-Opt-In)
        if getattr(self, "action", None) in ("create", "confirm"):
            return [permissions.AllowAny()]
        return super().get_permissions()


    def create(self, request, *args, **kwargs):
        # require consent_privacy True
        if not request.data.get("consent_privacy"):
            return Response({"detail": "Zustimmung zur Datenschutzerklärung erforderlich."}, status=400)
        response = super().create(request, *args, **kwargs)
        # send confirmation mail
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            confirm_token = response.data.get("confirm_token")
            frontend_base = getattr(settings, "FRONTEND_BASE_URL", "")
            confirm_url = f"{frontend_base}/confirm?token={confirm_token}"
            send_mail(
                "Bitte bestätigen Sie Ihre Kontaktanfrage",
                f"Hallo, bitte bestätigen Sie Ihre Anfrage: {confirm_url}",
                getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@mandari.local"),
                [response.data.get("email")],
            )
        except Exception:
            pass
        return response

    @action(detail=False, methods=["post"], url_path="confirm")
    def confirm(self, request):
        """Confirm via token, set confirmed_at."""
        token = request.data.get("token")
        if not token:
            return Response({"detail": "Token fehlt."}, status=400)
        lead = Lead.objects.filter(confirm_token=token).first()
        if not lead:
            return Response({"detail": "Ungültiger Token."}, status=404)
        if not lead.confirmed_at:
            from django.utils import timezone
            lead.confirmed_at = timezone.now()
            lead.save(update_fields=["confirmed_at", "updated_at"])
        return Response({"detail": "Bestätigt."})


class RoleAssignmentViewSet(viewsets.ModelViewSet):
	queryset = RoleAssignment.objects.all().select_related("user", "committee", "tenant")
	serializer_class = RoleAssignmentSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = __import__("core.models", fromlist=["Role"]).Role.objects.all().select_related("org")
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = __import__("core.models", fromlist=["UserRole"]).UserRole.objects.all().select_related("org", "user", "role")
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAdminUser]


class SubspaceViewSet(viewsets.ModelViewSet):
    queryset = Subspace.objects.all().select_related("tenant")
    serializer_class = SubspaceSerializer
    permission_classes = [permissions.IsAuthenticated]


class SpaceMembershipViewSet(viewsets.ModelViewSet):
    queryset = SpaceMembership.objects.all().select_related("subspace", "user")
    serializer_class = SpaceMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        subspace_id = self.request.query_params.get("subspace")
        user_id = self.request.query_params.get("user")
        org_id = self.request.query_params.get("org")
        if subspace_id:
            qs = qs.filter(subspace_id=subspace_id)
        if user_id:
            qs = qs.filter(user_id=user_id)
        if org_id:
            qs = qs.filter(subspace__tenant_id=org_id)
        return qs


class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all().select_related("org", "plan")
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]


class UsageMeterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UsageMeter.objects.all().select_related("org")
    serializer_class = UsageMeterSerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]


class FeatureFlagViewSet(viewsets.ModelViewSet):
    queryset = FeatureFlag.objects.all().select_related("org", "subspace")
    serializer_class = FeatureFlagSerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all().select_related("org", "subspace")
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorkflowConfigViewSet(viewsets.ModelViewSet):
    queryset = WorkflowConfig.objects.all().select_related("org", "subspace")
    serializer_class = WorkflowConfigSerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().select_related("org", "actor")
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]

    def get_queryset(self):
        qs = super().get_queryset()
        org_id = self.request.query_params.get("org")
        actor = self.request.query_params.get("actor")
        action = self.request.query_params.get("action")
        since = self.request.query_params.get("since")
        if org_id:
            qs = qs.filter(org_id=org_id)
        if actor:
            qs = qs.filter(actor_id=actor)
        if action:
            qs = qs.filter(action=action)
        if since:
            try:
                qs = qs.filter(at__gte=since)
            except Exception:
                pass
        return qs


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    queryset = WebhookEndpoint.objects.all().select_related("org")
    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]


class ApiKeyViewSet(viewsets.ModelViewSet):
    queryset = ApiKey.objects.all().select_related("org")
    serializer_class = ApiKeySerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]


class OAuthClientViewSet(viewsets.ModelViewSet):
    queryset = __import__("core.models", fromlist=["OAuthClient"]).OAuthClient.objects.all().select_related("org")
    serializer_class = OAuthClientSerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]


class MembershipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Membership.objects.all().select_related("org", "user")
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        org_id = self.request.query_params.get("org")
        user_id = self.request.query_params.get("user")
        if org_id:
            qs = qs.filter(org_id=org_id)
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all().select_related("user")
    serializer_class = StaffProfileSerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]


class OfferDraftViewSet(viewsets.ModelViewSet):
    queryset = OfferDraft.objects.all().select_related("org", "created_by")
    serializer_class = OfferDraftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=getattr(self.request, "user", None))

    def get_queryset(self):
        qs = super().get_queryset()
        lead = self.request.query_params.get("lead")
        status = self.request.query_params.get("status")
        org = self.request.query_params.get("org")
        if lead:
            qs = qs.filter(lead_id=lead)
        if status:
            qs = qs.filter(status=status)
        if org:
            qs = qs.filter(org_id=org)
        return qs

    @action(detail=False, methods=["post"], url_path="create-test-org", permission_classes=[permissions.IsAdminUser, AdminMfaRequired])
    def create_test_org(self, request):
        """Erzeugt eine Test-Organisation (Mandant) mit Standard-Subspace."""
        name = request.data.get("name") or "Test Org"
        slug = (request.data.get("slug") or f"test-{__import__('uuid').uuid4().hex[:8]}").lower()
        tenant = Tenant.objects.create(name=name, slug=slug)
        Subspace.objects.create(tenant=tenant, name="Test", key="test")
        AuditLog.objects.create(org=tenant, actor=request.user if request.user.is_authenticated else None, action="org.test_created", target_type="tenant", target_id=str(tenant.id), diff_json={"slug": slug})
        return Response(TenantSerializer(tenant).data, status=201)

class OrgsAdminViewSet(viewsets.ModelViewSet):
    """Admin-spezifische Endpunkte für Organisationen (Mandanten)."""
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAdminUser, AdminMfaRequired]

    def perform_create(self, serializer):
        tenant = serializer.save()
        # Standard-Subspace anlegen
        try:
            Subspace.objects.create(tenant=tenant, name="Hauptgremium", key="main")
        except Exception:
            pass
        # Audit-Log schreiben
        try:
            AuditLog.objects.create(org=tenant, actor=getattr(self.request, "user", None), action="org.created", target_type="tenant", target_id=str(tenant.id), diff_json={"name": tenant.name, "slug": tenant.slug})
        except Exception:
            pass

    @action(detail=True, methods=["post"], url_path="deactivate")
    def admin_deactivate(self, request, pk=None):
        tenant = self.get_object()
        tenant.is_active = False
        tenant.save(update_fields=["is_active"])
        AuditLog.objects.create(org=tenant, actor=request.user if request.user.is_authenticated else None, action="org.deactivated", target_type="tenant", target_id=str(tenant.id), diff_json={})
        return Response({"detail": "Deaktiviert"})

    @action(detail=True, methods=["post"], url_path="reactivate")
    def admin_reactivate(self, request, pk=None):
        tenant = self.get_object()
        tenant.is_active = True
        tenant.save(update_fields=["is_active"])
        AuditLog.objects.create(org=tenant, actor=request.user if request.user.is_authenticated else None, action="org.reactivated", target_type="tenant", target_id=str(tenant.id), diff_json={})
        return Response({"detail": "Reaktiviert"})

    @action(detail=True, methods=["post"], url_path="subscription")
    def set_subscription(self, request, pk=None):
        tenant = self.get_object()
        plan_id = request.data.get("plan") or request.data.get("plan_id")
        start = request.data.get("start_at")
        from django.utils import timezone
        from datetime import timedelta
        if not plan_id:
            return Response({"detail": "plan_id fehlt"}, status=400)
        plan = Plan.objects.filter(id=plan_id).first()
        if not plan:
            return Response({"detail": "Plan nicht gefunden"}, status=404)
        period_start = timezone.now() if not start else timezone.datetime.fromisoformat(start)
        period_end = period_start + timedelta(days=30)
        sub, _ = Subscription.objects.update_or_create(org=tenant, defaults={
            "plan": plan,
            "status": "active",
            "period_start": period_start,
            "period_end": period_end,
        })
        AuditLog.objects.create(org=tenant, actor=request.user if request.user.is_authenticated else None, action="plan.changed", target_type="subscription", target_id=str(sub.id), diff_json={"plan": plan.id})
        return Response(SubscriptionSerializer(sub).data)

    @action(detail=True, methods=["get"], url_path="usage")
    def get_usage(self, request, pk=None):
        tenant = self.get_object()
        meters = UsageMeter.objects.filter(org=tenant).order_by("-window_start")[:100]
        return Response(UsageMeterSerializer(meters, many=True).data)

    @action(detail=True, methods=["get", "post"], url_path="subspaces")
    def subspaces(self, request, pk=None):
        tenant = self.get_object()
        if request.method.lower() == "get":
            qs = Subspace.objects.filter(tenant=tenant)
            return Response(SubspaceSerializer(qs, many=True).data)
        # POST create
        serializer = SubspaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(tenant=tenant)
        AuditLog.objects.create(org=tenant, actor=request.user if request.user.is_authenticated else None, action="space.created", target_type="subspace", target_id=str(obj.id), diff_json={"key": obj.key})
        return Response(SubspaceSerializer(obj).data, status=201)

    @action(detail=True, methods=["post"], url_path="feature-flags")
    def feature_flags(self, request, pk=None):
        tenant = self.get_object()
        key = request.data.get("key")
        enabled = request.data.get("enabled")
        subspace_id = request.data.get("subspace_id")
        if key is None or enabled is None:
            return Response({"detail": "key und enabled erforderlich"}, status=400)
        ff, _ = FeatureFlag.objects.update_or_create(
            org=tenant,
            subspace_id=subspace_id,
            key=key,
            defaults={"enabled": bool(enabled)},
        )
        AuditLog.objects.create(org=tenant, actor=request.user if request.user.is_authenticated else None, action="feature.flag.updated", target_type="feature_flag", target_id=str(ff.id), diff_json={"key": key, "enabled": bool(enabled)})
        return Response(FeatureFlagSerializer(ff).data)

    @action(detail=True, methods=["get", "post", "delete"], url_path="pricing")
    def pricing(self, request, pk=None):
        """Verwalte Preisvereinbarungen.

        GET: Liste der Agreements (org + subspaces)
        POST: upsert {amount_cents, currency?, period?, subspace_id?}
        DELETE: {id}
        """
        tenant = self.get_object()
        if request.method.lower() == "get":
            agreements = PricingAgreement.objects.filter(org=tenant).select_related("subspace")
            return Response(PricingAgreementSerializer(agreements, many=True).data)
        if request.method.lower() == "delete":
            pricing_id = request.data.get("id")
            obj = PricingAgreement.objects.filter(id=pricing_id, org=tenant).first()
            if not obj:
                return Response({"detail": "Nicht gefunden"}, status=404)
            obj.delete()
            return Response({"detail": "Gelöscht"})
        # POST
        amount_cents = request.data.get("amount_cents")
        currency = request.data.get("currency", "EUR")
        period = request.data.get("period", "monthly")
        subspace_id = request.data.get("subspace_id")
        if amount_cents is None:
            return Response({"detail": "amount_cents erforderlich"}, status=400)
        obj, _ = PricingAgreement.objects.update_or_create(
            org=tenant,
            subspace_id=subspace_id,
            currency=currency,
            period=period,
            defaults={"amount_cents": int(amount_cents)},
        )
        return Response(PricingAgreementSerializer(obj).data, status=201)

    @action(detail=True, methods=["get", "post"], url_path="invitations")
    def invitations(self, request, pk=None):
        tenant = self.get_object()
        if request.method.lower() == "get":
            qs = Invitation.objects.filter(org=tenant)
            return Response(InvitationSerializer(qs, many=True).data)
        # Default Ablauf in 7 Tagen, wenn nicht gesetzt
        payload = dict(request.data)
        if not payload.get("expires_at"):
            from django.utils import timezone
            from datetime import timedelta
            payload["expires_at"] = (timezone.now() + timedelta(days=7)).isoformat()
        serializer = InvitationSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        inv = serializer.save(org=tenant)
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")
            url = f"{base}/accept-invite?token={inv.token}"
            send_mail("Einladung", f"Sie wurden eingeladen: {url}", getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@mandari.local"), [inv.email])
        except Exception:
            pass
        AuditLog.objects.create(org=tenant, actor=request.user if request.user.is_authenticated else None, action="invite.created", target_type="invitation", target_id=str(inv.id), diff_json={"email": inv.email})
        return Response(InvitationSerializer(inv).data, status=201)

    @action(detail=True, methods=["post"], url_path="invitations/(?P<invite_id>[^/.]+)/resend")
    def invitations_resend(self, request, pk=None, invite_id=None):
        tenant = self.get_object()
        inv = Invitation.objects.filter(org=tenant, id=invite_id).first()
        if not inv:
            return Response({"detail": "Nicht gefunden"}, status=404)
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")
            url = f"{base}/accept-invite?token={inv.token}"
            send_mail("Einladung", f"Sie wurden eingeladen: {url}", getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@mandari.local"), [inv.email])
        except Exception:
            pass
        AuditLog.objects.create(org=tenant, actor=request.user if request.user.is_authenticated else None, action="invite.resent", target_type="invitation", target_id=str(inv.id), diff_json={"email": inv.email})
        return Response({"detail": "Neu versendet"})

    @action(detail=True, methods=["post"], url_path="invitations/(?P<invite_id>[^/.]+)/cancel")
    def invitations_cancel(self, request, pk=None, invite_id=None):
        tenant = self.get_object()
        inv = Invitation.objects.filter(org=tenant, id=invite_id).first()
        if not inv:
            return Response({"detail": "Nicht gefunden"}, status=404)
        inv.delete()
        AuditLog.objects.create(org=tenant, actor=request.user if request.user.is_authenticated else None, action="invite.canceled", target_type="invitation", target_id=str(invite_id), diff_json={})
        return Response({"detail": "Storniert"})

    @action(detail=True, methods=["post"], url_path="members/(?P<user_id>[^/.]+)/role")
    def set_member_role(self, request, pk=None, user_id=None):
        tenant = self.get_object()
        role = request.data.get("role")
        if not role:
            return Response({"detail": "role erforderlich"}, status=400)
        mem, _ = Membership.objects.update_or_create(org=tenant, user_id=user_id, defaults={"role": role})
        AuditLog.objects.create(org=tenant, actor=request.user if request.user.is_authenticated else None, action="member.role.changed", target_type="membership", target_id=str(mem.id), diff_json={"role": role})
        return Response(MembershipSerializer(mem).data)


UserModel = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
	"""Einfache User-API mit Mandanten-Scope. Nur Admins dürfen global zugreifen.

	Für Nicht-Superuser wird automatisch nach `request.user.tenant` gefiltert.
	"""
	queryset = UserModel.objects.all()
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		qs = super().get_queryset()
		user = self.request.user
		if not user.is_superuser and getattr(user, "tenant_id", None):
			qs = qs.filter(tenant_id=user.tenant_id)
		return qs

	class SerializerClass(serializers.ModelSerializer):
		class Meta:
			model = UserModel
			fields = ["id", "username", "first_name", "last_name", "email", "tenant", "role", "is_active", "is_staff"]

	serializer_class = SerializerClass

	@action(detail=True, methods=["post"], url_path="set-password", permission_classes=[permissions.IsAdminUser])
	def set_password(self, request, pk=None):
		new_password = request.data.get("new_password")
		if not new_password or len(str(new_password)) < 8:
			return Response({"detail": "Passwort zu kurz (min. 8 Zeichen)."}, status=400)
		user = self.get_object()
		user.set_password(str(new_password))
		user.save(update_fields=["password"])
		return Response({"detail": "Passwort aktualisiert."})


class AuthViewSet(viewsets.ViewSet):
	permission_classes = [permissions.AllowAny]

	def _verify_totp(self, secret_base32: str, code: str) -> bool:
		try:
			import base64, hmac, hashlib, time, struct
			if not secret_base32 or not code:
				return False
			secret_padded = secret_base32.upper()
			missing = (-len(secret_padded)) % 8
			if missing:
				secret_padded = secret_padded + ("=" * missing)
			key = base64.b32decode(secret_padded)
			timestep = 30
			counter = int(time.time() // timestep)
			for offset in (-1, 0, 1):
				c = counter + offset
				msg = struct.pack('>Q', c)
				h = hmac.new(key, msg, hashlib.sha1).digest()
				o = h[-1] & 0x0F
				binary = ((h[o] & 0x7f) << 24) | (h[o+1] << 16) | (h[o+2] << 8) | (h[o+3])
				otp = str(binary % 1000000).zfill(6)
				if otp == str(code).zfill(6):
					return True
			return False
		except Exception:
			return False

	@action(detail=False, methods=["post"], url_path="login")
	def login_view(self, request):
		username = request.data.get("username")
		password = request.data.get("password")
		user = authenticate(request, username=username, password=password)
		if user is None:
			return Response({"detail": "Ungültige Zugangsdaten"}, status=400)
		# Wenn MFA für Nutzer aktiv: TOTP oder Recovery verlangen
		if getattr(user, "mfa_enabled", False):
			otp = request.data.get("otp")
			recovery = request.data.get("recovery_code")
			ok = False
			if otp and self._verify_totp(getattr(user, "mfa_secret", ""), str(otp)):
				ok = True
			elif recovery and recovery in (getattr(user, "mfa_recovery_codes", []) or []):
				codes = list(getattr(user, "mfa_recovery_codes", []) or [])
				codes.remove(recovery)
				user.mfa_recovery_codes = codes
				user.save(update_fields=["mfa_recovery_codes"])
				ok = True
			if not ok:
				return Response({"detail": "MFA erforderlich oder ungültig", "code": "MFA_REQUIRED"}, status=401)
		# Policy: Adminrolle ohne MFA blocken
		tenant = getattr(user, "tenant", None)
		is_admin_role = getattr(user, "role", "member") in ("staff", "faction_admin") or user.is_staff or user.is_superuser
		if tenant and tenant.mfa_required_for_admins and is_admin_role and not getattr(user, "mfa_enabled", False):
			return Response({"detail": "MFA erforderlich"}, status=412)
		login(request, user)
		return Response({"detail": "Eingeloggt"})

    @action(detail=False, methods=["post"], url_path="token")
    def token(self, request):
        """OAuth2 Token: grant_type=password|client_credentials → JWT (HS256).

        Response: {access_token, token_type, expires_in}
        """
        import os, jwt, uuid
        from datetime import datetime, timedelta, timezone
        grant_type = request.data.get("grant_type")
        if grant_type not in ("password", "client_credentials"):
            return Response({"error": "unsupported_grant_type"}, status=400)

        audience = os.getenv("JWT_AUDIENCE", "mandari-api")
        issuer = os.getenv("JWT_ISSUER", "mandari")
        lifetime_s = int(os.getenv("JWT_LIFETIME_SECONDS", "3600"))
        secret = os.getenv("JWT_SECRET", os.getenv("DJANGO_SECRET_KEY", "insecure"))
        now = datetime.now(tz=timezone.utc)
        exp = now + timedelta(seconds=lifetime_s)

        scopes: list[str] = []
        sub = None
        org_id = None

        if grant_type == "password":
            username = request.data.get("username")
            password = request.data.get("password")
            if not username or not password:
                return Response({"error": "invalid_request"}, status=400)
            user = authenticate(request, username=username, password=password)
            if user is None:
                return Response({"error": "invalid_grant"}, status=400)
            # MFA-Policy: falls aktiv und ohne gültige Session, optional restriktiver gestalten
            sub = str(user.id)
            org_id = getattr(user, "tenant_id", None)
            scopes = ["user"]

        if grant_type == "client_credentials":
            client_id = request.data.get("client_id")
            client_secret = request.data.get("client_secret")
            if not client_id or not client_secret:
                return Response({"error": "invalid_request"}, status=400)
            from core.models import OAuthClient
            client = OAuthClient.objects.filter(client_id=client_id, is_active=True).select_related("org").first()
            if not client or not client.check_secret(client_secret):
                return Response({"error": "invalid_client"}, status=401)
            sub = f"client:{client.id}"
            org_id = client.org_id
            scopes = list(client.scopes or [])
            client.last_used_at = now
            client.save(update_fields=["last_used_at"])

        payload = {
            "iss": issuer,
            "aud": audience,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "jti": uuid.uuid4().hex,
            "sub": sub,
            "org_id": org_id,
            "scopes": scopes,
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        return Response({"access_token": token, "token_type": "bearer", "expires_in": lifetime_s})


class OrgViewSet(viewsets.ViewSet):
    """Schlankes Tenant-Profil basierend auf aktueller Org (aus Session/JWT/Host)."""
    permission_classes = [permissions.IsAuthenticated]

    def _resolve_tenant(self, request):
        hint = getattr(request, "tenant_hint", None)
        from core.models import Tenant, OParlSource
        t = None
        if hint:
            t = Tenant.objects.filter(domain=hint).first() or Tenant.objects.filter(slug=hint).first()
        if not t and getattr(request, "user", None):
            t = getattr(request.user, "tenant", None)
        return t

    def _serialize(self, tenant):
        from core.models import OParlSource
        sources = list(OParlSource.objects.filter(tenant=tenant).values("id", "root_url", "enabled", "last_synced_at"))
        return {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "domain": tenant.domain,
            "logo_url": tenant.logo_url,
            "color_primary": tenant.color_primary,
            "color_secondary": tenant.color_secondary,
            "mfa_required_for_admins": tenant.mfa_required_for_admins,
            "region": tenant.region,
            "oparl_sources": sources,
            "ai_limits": {},
        }

    def list(self, request):
        tenant = self._resolve_tenant(request)
        if not tenant:
            return Response({"detail": "Tenant nicht gefunden"}, status=404)
        return Response(self._serialize(tenant))

    def partial_update(self, request, pk=None):
        tenant = self._resolve_tenant(request)
        if not tenant:
            return Response({"detail": "Tenant nicht gefunden"}, status=404)
        # Nur bestimmte Felder erlauben
        allowed = {"name", "logo_url", "color_primary", "color_secondary", "domain", "region", "mfa_required_for_admins"}
        updates = {k: v for k, v in request.data.items() if k in allowed}
        if updates:
            for k, v in updates.items():
                setattr(tenant, k, v)
            tenant.save(update_fields=list(updates.keys()))
            try:
                AuditLog.objects.create(org=tenant, actor=getattr(request, "user", None), action="org.updated", target_type="tenant", target_id=str(tenant.id), diff_json=updates)
            except Exception:
                pass
        return Response(self._serialize(tenant))

	@action(detail=False, methods=["post"], url_path="accept-invite")
	def accept_invite(self, request):
		"""Invite mittels Token akzeptieren: erstellt Membership und optional SpaceMemberships."""
		token = request.data.get("token")
		username = request.data.get("username")
		password = request.data.get("password")
		if not token or not username or not password:
			return Response({"detail": "token, username, password erforderlich"}, status=400)
		inv = Invitation.objects.filter(token=token).first()
		if not inv:
			return Response({"detail": "Ungültige Einladung"}, status=404)
		from django.utils import timezone
		if inv.expires_at and inv.expires_at < timezone.now():
			return Response({"detail": "Einladung abgelaufen"}, status=400)
		UserModel = get_user_model()
		user = UserModel.objects.filter(username=username).first()
		if user is None:
			user = UserModel.objects.create_user(username=username, password=password, email=inv.email, tenant=inv.org)
		# Org membership
		Membership.objects.update_or_create(org=inv.org, user=user, defaults={"role": inv.role})
		# Space roles
		for item in (inv.subspace_roles or []):
			sub_id = item.get("subspace_id")
			role = item.get("role") or "member"
			if sub_id:
				SpaceMembership.objects.update_or_create(subspace_id=sub_id, user=user, defaults={"role": role})
		inv.accepted_at = timezone.now()
		inv.save(update_fields=["accepted_at"])
		inv.delete()
		return Response({"detail": "Einladung akzeptiert"})

	@action(detail=False, methods=["post"], url_path="logout")
	def logout_view(self, request):
		logout(request)
		return Response({"detail": "Ausgeloggt"})

	@action(detail=False, methods=["get"], url_path="me", permission_classes=[permissions.IsAuthenticated])
	def me(self, request):
		user = request.user
		return Response({
			"id": user.id,
			"username": user.username,
			"tenant": getattr(user, "tenant_id", None),
			"role": getattr(user, "role", None),
			"is_staff": user.is_staff,
			"is_superuser": user.is_superuser,
			"mfa_enabled": getattr(user, "mfa_enabled", False),
		})

	@action(detail=False, methods=["post"], url_path="password-reset-request")
	def password_reset_request(self, request):
		serializer = PasswordResetRequestSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		email = serializer.validated_data["email"]
		user = UserModel.objects.filter(email=email).first()
		# Immer 200 antworten (Datensparsamkeit), Token nur erzeugen wenn User existiert
		if user:
			from django.utils import timezone
			token_obj = PasswordResetToken.objects.create(
				user=user,
				expires_at=timezone.now() + timezone.timedelta(hours=1),
			)
			# Mail versenden
			try:
				from django.core.mail import send_mail
				from django.conf import settings
				frontend_base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5174")
				url = f"{frontend_base}/reset?token={token_obj.token}"
				send_mail(
					"Passwort zurücksetzen",
					f"Sie können Ihr Passwort hier zurücksetzen: {url}",
					getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@mandari.local"),
					[email],
				)
			except Exception:
				pass
		return Response({"detail": "Wenn die E-Mail existiert, wurde ein Link versendet."})

	@action(detail=False, methods=["post"], url_path="password-reset-confirm")
	def password_reset_confirm(self, request):
		serializer = PasswordResetConfirmSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		token = serializer.validated_data["token"]
		new_password = serializer.validated_data["new_password"]
		from django.utils import timezone
		token_obj = PasswordResetToken.objects.filter(token=token).select_related("user").first()
		if not token_obj or not token_obj.is_valid:
			return Response({"detail": "Ungültiger oder abgelaufener Token."}, status=400)
		user = token_obj.user
		user.set_password(new_password)
		user.save(update_fields=["password"])
		token_obj.used_at = timezone.now()
		token_obj.save(update_fields=["used_at"])
		return Response({"detail": "Passwort aktualisiert."})

	@action(detail=False, methods=["post"], url_path="mfa/setup", permission_classes=[permissions.IsAuthenticated])
	def mfa_setup(self, request):
		"""Erzeugt Base32-TOTP-Secret, otpauth-URL und Recovery-Codes."""
		import secrets, base64, urllib.parse
		user = request.user
		secret_bytes = secrets.token_bytes(10)
		secret = base64.b32encode(secret_bytes).decode("utf-8").rstrip("=")
		recovery = [secrets.token_hex(4) for _ in range(8)]
		user.mfa_secret = secret
		user.mfa_recovery_codes = recovery
		user.save(update_fields=["mfa_secret", "mfa_recovery_codes"])
		issuer = urllib.parse.quote("Mandari")
		account = urllib.parse.quote(getattr(user, "username", "user"))
		otpauth = f"otpauth://totp/{issuer}:{account}?secret={secret}&issuer={issuer}&digits=6&period=30"
		return Response({"secret": secret, "recovery_codes": recovery, "otpauth_url": otpauth})

	@action(detail=False, methods=["post"], url_path="mfa/enable", permission_classes=[permissions.IsAuthenticated])
	def mfa_enable(self, request):
		user = request.user
		otp = request.data.get("otp")
		if not user.mfa_secret or not otp or not self._verify_totp(user.mfa_secret, str(otp)):
			return Response({"detail": "TOTP ungültig"}, status=400)
		user.mfa_enabled = True
		user.save(update_fields=["mfa_enabled"])
		return Response({"detail": "MFA aktiviert"})

	@action(detail=False, methods=["post"], url_path="mfa/disable", permission_classes=[permissions.IsAuthenticated])
	def mfa_disable(self, request):
		user = request.user
		user.mfa_enabled = False
		user.mfa_secret = ""
		user.mfa_recovery_codes = []
		user.save(update_fields=["mfa_enabled", "mfa_secret", "mfa_recovery_codes"])
		return Response({"detail": "MFA deaktiviert"})

	@action(detail=False, methods=["post"], url_path="mfa/verify", permission_classes=[permissions.IsAuthenticated])
	def mfa_verify(self, request):
		user = request.user
		otp = request.data.get("otp")
		recovery = request.data.get("recovery_code")
		from django.utils import timezone
		if otp and self._verify_totp(getattr(user, "mfa_secret", ""), str(otp)):
			user.mfa_last_verified_at = timezone.now()
			user.save(update_fields=["mfa_last_verified_at"])
			return Response({"detail": "OK"})
		if recovery and recovery in (getattr(user, "mfa_recovery_codes", []) or []):
			codes = list(getattr(user, "mfa_recovery_codes", []) or [])
			codes.remove(recovery)
			user.mfa_recovery_codes = codes
			user.mfa_last_verified_at = timezone.now()
			user.save(update_fields=["mfa_recovery_codes", "mfa_last_verified_at"])
			return Response({"detail": "OK"})
		return Response({"detail": "Ungültig"}, status=400)


# ==========================
# OParl API (read-only, Feature-Flag gesteuert)
# ==========================

def _resolve_tenant_from_request(request):
	"""Ermittle Tenant aus Host, Header X-Tenant oder ?tenant= Parameter."""
	host = request.get_host().split(":")[0]
	slug_or_domain = request.headers.get("X-Tenant") or request.query_params.get("tenant") or host
	tenant = Tenant.objects.filter(domain=slug_or_domain).first() or Tenant.objects.filter(slug=slug_or_domain).first()
	return tenant


def _assert_oparl_enabled(tenant):
	"""Wirf 404 wenn OParl-API nicht aktiviert ist."""
	if not tenant:
		from django.http import Http404
		raise Http404("Tenant nicht gefunden")
	enabled = FeatureFlag.objects.filter(org=tenant, subspace__isnull=True, key="oparl_api", enabled=True).exists()
	if not enabled:
		from django.http import Http404
		raise Http404("OParl nicht aktiviert")


class OParlBodiesViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Organization.objects.all()
	permission_classes = [permissions.AllowAny]

	def list(self, request, *args, **kwargs):
		tenant = _resolve_tenant_from_request(request)
		_assert_oparl_enabled(tenant)
		qs = self.get_queryset().filter(tenant=tenant)
		items = [{
			"id": o.id,
			"name": o.name,
			"oparl_id": o.oparl_id,
		} for o in qs[:200]]
		return Response(items)


class OParlMeetingsViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Meeting.objects.all().select_related("committee")
	permission_classes = [permissions.AllowAny]

	def list(self, request, *args, **kwargs):
		tenant = _resolve_tenant_from_request(request)
		_assert_oparl_enabled(tenant)
		qs = self.get_queryset().filter(tenant=tenant).order_by("-start")
		items = [{
			"id": m.id,
			"committee": m.committee_id,
			"start": m.start,
			"end": m.end,
			"oparl_id": m.oparl_id,
		} for m in qs[:200]]
		return Response(items)


class OParlPapersViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Document.objects.all().select_related("agenda_item")
	permission_classes = [permissions.AllowAny]

	def list(self, request, *args, **kwargs):
		tenant = _resolve_tenant_from_request(request)
		_assert_oparl_enabled(tenant)
		qs = self.get_queryset().filter(tenant=tenant).order_by("-created_at")
		items = [{
			"id": d.id,
			"title": d.title,
			"oparl_id": d.oparl_id,
			"created_at": d.created_at,
		} for d in qs[:200]]
		return Response(items)
