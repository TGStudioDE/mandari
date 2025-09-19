import os
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from rest_framework.decorators import action
from .models import AgendaItem, Committee, Document, Meeting, Motion, OParlSource, Organization, Person, ShareLink, Team, TeamMembership, Tenant
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

    def create(self, request, *args, **kwargs):
        up = _upsert_create(self, Committee, request)
        if up is not None:
            return up
        return super().create(request, *args, **kwargs)


class PersonViewSet(BaseTenantViewSet):
	queryset = Person.objects.all()
	serializer_class = PersonSerializer

    def create(self, request, *args, **kwargs):
        up = _upsert_create(self, Person, request)
        if up is not None:
            return up
        return super().create(request, *args, **kwargs)


class OrganizationViewSet(BaseTenantViewSet):
	queryset = Organization.objects.all()
	serializer_class = OrganizationSerializer

    def create(self, request, *args, **kwargs):
        up = _upsert_create(self, Organization, request)
        if up is not None:
            return up
        return super().create(request, *args, **kwargs)


class MeetingViewSet(BaseTenantViewSet):
	queryset = Meeting.objects.all().select_related("committee")
	serializer_class = MeetingSerializer

    def create(self, request, *args, **kwargs):
        up = _upsert_create(self, Meeting, request)
        if up is not None:
            return up
        return super().create(request, *args, **kwargs)


class AgendaItemViewSet(BaseTenantViewSet):
	queryset = AgendaItem.objects.all().select_related("meeting")
	serializer_class = AgendaItemSerializer

    def create(self, request, *args, **kwargs):
        up = _upsert_create(self, AgendaItem, request)
        if up is not None:
            return up
        return super().create(request, *args, **kwargs)


class DocumentViewSet(BaseTenantViewSet):
	queryset = Document.objects.all().select_related("agenda_item")
	serializer_class = DocumentSerializer

	def create(self, request, *args, **kwargs):
        content_hash = request.data.get("content_hash")
        tenant_id = request.data.get("tenant")
        oparl_id = request.data.get("oparl_id")
        source_base = request.data.get("source_base", "")
        if content_hash and tenant_id:
            existing = Document.objects.filter(tenant_id=tenant_id, content_hash=content_hash).first()
            if existing:
                ser = self.get_serializer(existing)
                return Response(ser.data, status=status.HTTP_200_OK)
        if tenant_id and oparl_id and source_base:
            existing = Document.objects.filter(
                tenant_id=tenant_id, oparl_id=oparl_id, source_base=source_base
            ).first()
            if existing:
                serializer = self.get_serializer(existing, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)


def _upsert_create(viewset, model_cls, request):
    tenant_id = request.data.get("tenant")
    oparl_id = request.data.get("oparl_id")
    source_base = request.data.get("source_base", "")
    if tenant_id and oparl_id and source_base:
        existing = model_cls.objects.filter(
            tenant_id=tenant_id, oparl_id=oparl_id, source_base=source_base
        ).first()
        if existing:
            serializer = viewset.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            viewset.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
    return None


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
				r = client.post(
					f"{base}/oparl/ingest",
					params={
						"root": source.root_url,
						"tenant_id": source.tenant_id,
						"source_id": source.id,
						"source_base": source.root_url,
					},
				)
				return Response(r.json(), status=r.status_code)
		except Exception as e:
			return Response({"error": str(e)}, status=500)

