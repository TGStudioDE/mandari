from django.http import HttpResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
	AgendaItemViewSet,
	AuthViewSet,
	CommitteeViewSet,
	DocumentViewSet,
	LeadViewSet,
	MeetingViewSet,
	MotionViewSet,
    OParlSourceViewSet,
	OrganizationViewSet,
	PersonViewSet,
	RoleAssignmentViewSet,
	ShareLinkViewSet,
    TeamMembershipViewSet,
    TeamViewSet,
	UserViewSet,
	TenantViewSet,
)

router = DefaultRouter()
router.register(r"tenants", TenantViewSet)
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"committees", CommitteeViewSet)
router.register(r"persons", PersonViewSet)
router.register(r"organizations", OrganizationViewSet)
router.register(r"meetings", MeetingViewSet)
router.register(r"agenda-items", AgendaItemViewSet)
router.register(r"documents", DocumentViewSet)
router.register(r"leads", LeadViewSet, basename="lead")
router.register(r"motions", MotionViewSet)
router.register(r"share-links", ShareLinkViewSet)
router.register(r"teams", TeamViewSet)
router.register(r"team-memberships", TeamMembershipViewSet)
router.register(r"oparl-sources", OParlSourceViewSet)
router.register(r"role-assignments", RoleAssignmentViewSet)
router.register(r"users", UserViewSet)

urlpatterns = [
	path("", include(router.urls)),
    path(
        "calendar/tenant/<int:tenant_id>.ics",
        lambda request, tenant_id: HttpResponse(
            __import__("core.ical", fromlist=["export_meetings_ics"]).export_meetings_ics(
                __import__("core.models", fromlist=["Meeting"]).Meeting.objects.filter(tenant_id=tenant_id)
            ),
            content_type="text/calendar",
        ),
        name="tenant-ics",
    ),
]

