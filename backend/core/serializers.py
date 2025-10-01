from rest_framework import serializers

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
    OAuthClient,
    PricingAgreement,
    Membership,
    Invitation,
    StaffProfile,
    OfferDraft,
    Role,
    UserRole,
)


class TenantSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tenant
		fields = [
			"id",
			"name",
			"slug",
			"domain",
			"is_active",
			"region",
			"mfa_required_for_admins",
			"logo_url",
			"color_primary",
			"color_secondary",
		]


class CommitteeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Committee
		fields = ["id", "tenant", "name", "oparl_id", "organization"]


class PersonSerializer(serializers.ModelSerializer):
	class Meta:
		model = Person
		fields = ["id", "tenant", "name", "party", "oparl_id"]


class OrganizationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Organization
		fields = ["id", "tenant", "name", "oparl_id"]


class MeetingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Meeting
		fields = ["id", "tenant", "committee", "start", "end", "oparl_id"]


class AgendaItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = AgendaItem
		fields = ["id", "tenant", "meeting", "position", "title", "category", "oparl_id"]


class DocumentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Document
		fields = [
			"id",
			"tenant",
			"agenda_item",
			"title",
			"file",
			"raw",
			"normalized",
			"content_text",
			"content_hash",
			"oparl_id",
			"created_at",
			"updated_at",
		]


class MotionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Motion
		fields = ["id", "tenant", "author", "title", "status", "content", "version", "created_at", "updated_at"]


class ShareLinkSerializer(serializers.ModelSerializer):
	class Meta:
		model = ShareLink
		fields = ["id", "motion", "token", "expires_at", "can_edit"]


class TeamSerializer(serializers.ModelSerializer):
	class Meta:
		model = Team
		fields = ["id", "tenant", "name", "slug"]


class TeamMembershipSerializer(serializers.ModelSerializer):
	class Meta:
		model = TeamMembership
		fields = ["id", "team", "user", "role"]


class OParlSourceSerializer(serializers.ModelSerializer):
	class Meta:
		model = OParlSource
		fields = ["id", "tenant", "root_url", "enabled", "last_synced_at", "etag", "last_modified"]


class LeadSerializer(serializers.ModelSerializer):
	class Meta:
		model = Lead
		fields = [
			"id",
			"tenant",
			"company",
			"name",
			"email",
			"message",
			"consent_privacy",
			"consent_marketing",
			"confirm_token",
			"confirmed_at",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["confirm_token", "confirmed_at", "created_at", "updated_at"]


class RoleAssignmentSerializer(serializers.ModelSerializer):
	class Meta:
		model = RoleAssignment
		fields = ["id", "tenant", "user", "committee", "role"]


class PasswordResetRequestSerializer(serializers.Serializer):
	email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
	token = serializers.CharField()
	new_password = serializers.CharField(min_length=8)


# ==========================
# Admin-/SaaS-Serializer
# ==========================


class SubspaceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subspace
		fields = ["id", "tenant", "name", "key", "type", "domain", "settings_json"]


class SpaceMembershipSerializer(serializers.ModelSerializer):
	class Meta:
		model = SpaceMembership
		fields = ["id", "user", "subspace", "role"]


class PlanSerializer(serializers.ModelSerializer):
	class Meta:
		model = Plan
		fields = ["id", "code", "name", "features_json", "hard_limits_json", "soft_limits_json"]


class SubscriptionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subscription
		fields = [
			"id",
			"org",
			"plan",
			"status",
			"period_start",
			"period_end",
			"billing_account_id",
		]


class UsageMeterSerializer(serializers.ModelSerializer):
	class Meta:
		model = UsageMeter
		fields = ["id", "org", "metric", "window_start", "window_end", "value"]


class FeatureFlagSerializer(serializers.ModelSerializer):
	class Meta:
		model = FeatureFlag
		fields = ["id", "org", "subspace", "key", "enabled"]


class NoteSerializer(serializers.ModelSerializer):
	class Meta:
		model = Note
		fields = [
			"id",
			"org",
			"subspace",
			"title",
			"body",
			"tags",
			"related_entity",
			"visibility",
			"status",
			"created_at",
			"updated_at",
		]


class WorkflowConfigSerializer(serializers.ModelSerializer):
	class Meta:
		model = WorkflowConfig
		fields = ["id", "org", "subspace", "rules_json"]


class AuditLogSerializer(serializers.ModelSerializer):
	class Meta:
		model = AuditLog
		fields = ["id", "org", "actor", "action", "target_type", "target_id", "diff_json", "at"]


class WebhookEndpointSerializer(serializers.ModelSerializer):
	class Meta:
		model = WebhookEndpoint
		fields = ["id", "org", "url", "secret", "events", "enabled", "created_at"]
		extra_kwargs = {
			"secret": {"write_only": True},
		}


class ApiKeySerializer(serializers.ModelSerializer):
	token = serializers.CharField(write_only=True, required=False)

	class Meta:
		model = ApiKey
		fields = [
			"id",
			"org",
			"name",
			"scopes",
			"hashed_key",
			"expires_at",
			"created_at",
			"last_used_at",
			"token",
		]
		read_only_fields = ["hashed_key", "created_at", "last_used_at"]

	def create(self, validated_data):
		token = validated_data.pop("token", None)
		instance: ApiKey = ApiKey(**validated_data)
		if token:
			instance.set_plain_key(token)
		instance.save()
		# Plain-Token wird NICHT persistiert, nur zur Laufzeit zurückgegeben
		instance.token = token  # type: ignore[attr-defined]
		return instance


class OAuthClientSerializer(serializers.ModelSerializer):
	plain_secret = serializers.CharField(write_only=True, required=False)

	class Meta:
		model = OAuthClient
		fields = [
			"id",
			"org",
			"name",
			"client_id",
			"client_secret_hashed",
			"scopes",
			"is_active",
			"created_at",
			"last_used_at",
			"plain_secret",
		]
		read_only_fields = ["client_secret_hashed", "created_at", "last_used_at"]

	def create(self, validated_data):
		plain = validated_data.pop("plain_secret", None)
		from uuid import uuid4
		if not validated_data.get("client_id"):
			validated_data["client_id"] = uuid4().hex
		instance: OAuthClient = OAuthClient(**validated_data)
		if plain:
			instance.set_plain_secret(plain)
		instance.save()
		instance.plain_secret = plain  # type: ignore[attr-defined]
		return instance


class PricingAgreementSerializer(serializers.ModelSerializer):
	class Meta:
		model = PricingAgreement
		fields = [
			"id",
			"org",
			"subspace",
			"amount_cents",
			"currency",
			"period",
			"created_at",
			"updated_at",
		]


class MembershipSerializer(serializers.ModelSerializer):
	user_detail = serializers.SerializerMethodField()

	class Meta:
		model = Membership
		fields = ["id", "org", "user", "role", "user_detail"]

	def get_user_detail(self, obj):
		u = getattr(obj, "user", None)
		if not u:
			return None
		return {
			"id": u.id,
			"username": u.username,
			"email": u.email,
			"is_staff": u.is_staff,
		}


class InvitationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Invitation
		fields = [
			"id",
			"org",
			"email",
			"role",
			"subspace_roles",
			"token",
			"expires_at",
			"accepted_at",
			"created_at",
		]
		read_only_fields = ["token", "accepted_at", "created_at"]


class StaffProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = StaffProfile
		fields = ["id", "user", "department", "scopes", "can_create_test_env"]


class OfferDraftSerializer(serializers.ModelSerializer):
	class Meta:
		model = OfferDraft
		fields = [
			"id",
			"org",
			"lead",
			"title",
			"body",
			"customer_email",
			"amount_cents",
			"status",
			"next_step",
			"due_date",
			"created_by",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["created_by", "created_at", "updated_at"]


class RoleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Role
		fields = ["id", "org", "slug", "name", "description", "permissions"]


class UserRoleSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserRole
		fields = ["id", "org", "user", "role"]

