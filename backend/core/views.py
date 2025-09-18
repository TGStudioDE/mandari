import os
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from rest_framework.decorators import action
from .models import AgendaItem, Committee, Document, Lead, Meeting, Motion, OParlSource, Organization, Person, ShareLink, Team, TeamMembership, Tenant
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
	ShareLinkSerializer,
    TeamMembershipSerializer,
    TeamSerializer,
	TenantSerializer,
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


class CommitteeViewSet(BaseTenantViewSet):
	queryset = Committee.objects.all()
	serializer_class = CommitteeSerializer


class PersonViewSet(BaseTenantViewSet):
	queryset = Person.objects.all()
	serializer_class = PersonSerializer


class OrganizationViewSet(BaseTenantViewSet):
	queryset = Organization.objects.all()
	serializer_class = OrganizationSerializer


class MeetingViewSet(BaseTenantViewSet):
	queryset = Meeting.objects.all().select_related("committee")
	serializer_class = MeetingSerializer


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


class MotionViewSet(BaseTenantViewSet):
	queryset = Motion.objects.all().select_related("author")
	serializer_class = MotionSerializer


class ShareLinkViewSet(viewsets.ModelViewSet):
	queryset = ShareLink.objects.all().select_related("motion")
	serializer_class = ShareLinkSerializer
	permission_classes = [permissions.AllowAny]


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
				r = client.post(f"{base}/oparl/ingest", params={"root": source.root_url, "tenant_id": source.tenant_id})
				return Response(r.json(), status=r.status_code)
		except Exception as e:
			return Response({"error": str(e)}, status=500)


class LeadViewSet(viewsets.ModelViewSet):
	queryset = Lead.objects.all().order_by("-created_at")
	serializer_class = LeadSerializer
	permission_classes = [permissions.AllowAny]

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
