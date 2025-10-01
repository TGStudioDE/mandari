from django.http import HttpResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
	AgendaItemViewSet,
	AuthViewSet,
	CommitteeViewSet,
	DocumentViewSet,
	ApiKeyViewSet,
    OAuthClientViewSet,
	LeadViewSet,
	MeetingViewSet,
	MotionViewSet,
    OParlSourceViewSet,
	OrganizationViewSet,
	PersonViewSet,
	RoleAssignmentViewSet,
    RoleViewSet,
    UserRoleViewSet,
	ShareLinkViewSet,
    TeamMembershipViewSet,
    TeamViewSet,
	SubspaceViewSet,
	SpaceMembershipViewSet,
	PlanViewSet,
	SubscriptionViewSet,
	UsageMeterViewSet,
	FeatureFlagViewSet,
	NoteViewSet,
	WorkflowConfigViewSet,
	AuditLogViewSet,
	WebhookEndpointViewSet,
	MembershipViewSet,
	StaffProfileViewSet,
	OfferDraftViewSet,
	UserViewSet,
	TenantViewSet,
    OrgViewSet,
    OrgsAdminViewSet,
    OParlBodiesViewSet,
    OParlMeetingsViewSet,
    OParlPapersViewSet,
    SearchViewSet,
    AiViewSet,
)

router = DefaultRouter()
admin_router = DefaultRouter()
router.register(r"tenants", TenantViewSet)
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"subspaces", SubspaceViewSet)
router.register(r"space-memberships", SpaceMembershipViewSet)
router.register(r"plans", PlanViewSet)
router.register(r"subscriptions", SubscriptionViewSet)
router.register(r"usage", UsageMeterViewSet, basename="usage")
router.register(r"feature-flags", FeatureFlagViewSet)
router.register(r"notes", NoteViewSet)
router.register(r"workflow-configs", WorkflowConfigViewSet)
router.register(r"audit-logs", AuditLogViewSet, basename="audit-logs")
router.register(r"webhooks", WebhookEndpointViewSet)
router.register(r"api-keys", ApiKeyViewSet)
router.register(r"oauth-clients", OAuthClientViewSet)
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
# kompatibler Alias
router.register(r"connectors/oparl", OParlSourceViewSet, basename="connectors-oparl")
router.register(r"role-assignments", RoleAssignmentViewSet)
router.register(r"roles", RoleViewSet)
router.register(r"user-roles", UserRoleViewSet)
router.register(r"users", UserViewSet)
router.register(r"memberships", MembershipViewSet, basename="memberships")
router.register(r"staff", StaffProfileViewSet)
router.register(r"offer-drafts", OfferDraftViewSet)
router.register(r"org", OrgViewSet, basename="org")
router.register(r"search", SearchViewSet, basename="search")
router.register(r"ai", AiViewSet, basename="ai")

admin_router.register(r"orgs", OrgsAdminViewSet, basename="admin-orgs")
admin_router.register(r"plans", PlanViewSet, basename="admin-plans")
admin_router.register(r"subscriptions", SubscriptionViewSet, basename="admin-subscriptions")
admin_router.register(r"usage", UsageMeterViewSet, basename="admin-usage")
admin_router.register(r"feature-flags", FeatureFlagViewSet, basename="admin-feature-flags")
admin_router.register(r"notes", NoteViewSet, basename="admin-notes")
admin_router.register(r"workflow-configs", WorkflowConfigViewSet, basename="admin-workflow-configs")
admin_router.register(r"audit-logs", AuditLogViewSet, basename="admin-audit-logs")
admin_router.register(r"webhooks", WebhookEndpointViewSet, basename="admin-webhooks")
admin_router.register(r"api-keys", ApiKeyViewSet, basename="admin-api-keys")
admin_router.register(r"oauth-clients", OAuthClientViewSet, basename="admin-oauth-clients")

urlpatterns = [
	path("", include(router.urls)),
    path("admin/", include(admin_router.urls)),
    path("oparl/bodies", OParlBodiesViewSet.as_view({'get': 'list'}), name="oparl-bodies"),
    path("oparl/meetings", OParlMeetingsViewSet.as_view({'get': 'list'}), name="oparl-meetings"),
    path("oparl/papers", OParlPapersViewSet.as_view({'get': 'list'}), name="oparl-papers"),
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

