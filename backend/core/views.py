import os
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from rest_framework.decorators import action
from .models import AgendaItem, Committee, Document, Meeting, Motion, OParlSource, Organization, Person, ShareLink, Team, TeamMembership, Tenant, AIModelRegistry, AIProviderConfig, AIAllowedModel, AIPolicy, AIFeatureFlag, AIUsageLog
from .serializers import (
	AgendaItemSerializer,
	CommitteeSerializer,
	DocumentSerializer,
	MeetingSerializer,
	MotionSerializer,
    OParlSourceSerializer,
	OrganizationSerializer,
	PersonSerializer,
	ShareLinkSerializer,
    TeamMembershipSerializer,
    TeamSerializer,
	TenantSerializer,
    AIModelRegistrySerializer,
    AIProviderConfigSerializer,
    AIAllowedModelSerializer,
    AIPolicySerializer,
    AIFeatureFlagSerializer,
    AIUsageLogSerializer,
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


class AIModelRegistryViewSet(viewsets.ModelViewSet):
	queryset = AIModelRegistry.objects.all()
	serializer_class = AIModelRegistrySerializer
	permission_classes = [permissions.IsAdminUser]


class AIProviderConfigViewSet(BaseTenantViewSet):
	queryset = AIProviderConfig.objects.all()
	serializer_class = AIProviderConfigSerializer
	permission_classes = [permissions.IsAdminUser]

	@action(detail=True, methods=["post"], url_path="test-call")
	def test_call(self, request, pk=None):
		# Stub: führt einen No-PII Testprompt gegen konfigurierten Provider aus
		config = self.get_object()
		try:
			from core.ai.runtime import perform_test_call
			result = perform_test_call(config)
			return Response({"ok": True, "result": result})
		except Exception as e:
			return Response({"ok": False, "error": str(e)}, status=500)


class AIAllowedModelViewSet(BaseTenantViewSet):
	queryset = AIAllowedModel.objects.all()
	serializer_class = AIAllowedModelSerializer
	permission_classes = [permissions.IsAdminUser]


class AIPolicyViewSet(BaseTenantViewSet):
	queryset = AIPolicy.objects.all()
	serializer_class = AIPolicySerializer
	permission_classes = [permissions.IsAdminUser]


class AIFeatureFlagViewSet(BaseTenantViewSet):
	queryset = AIFeatureFlag.objects.all()
	serializer_class = AIFeatureFlagSerializer
	permission_classes = [permissions.IsAdminUser]


class AIUsageLogViewSet(BaseTenantViewSet):
	queryset = AIUsageLog.objects.all()
	serializer_class = AIUsageLogSerializer
	permission_classes = [permissions.IsAdminUser]
