from rest_framework import serializers

from .models import AgendaItem, Committee, Document, Meeting, Motion, OParlSource, Organization, Person, ShareLink, Team, TeamMembership, Tenant, AIModelRegistry, AIProviderConfig, AIAllowedModel, AIPolicy, AIFeatureFlag, AIUsageLog


class TenantSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tenant
		fields = ["id", "name", "slug", "domain"]


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


class AIModelRegistrySerializer(serializers.ModelSerializer):
	class Meta:
		model = AIModelRegistry
		fields = [
			"id",
			"name",
			"provider",
			"capability",
			"max_input_tokens",
			"max_output_tokens",
			"cost_prompt_mtokens",
			"cost_completion_mtokens",
			"metadata",
			"is_default",
		]


class AIProviderConfigSerializer(serializers.ModelSerializer):
	class Meta:
		model = AIProviderConfig
		fields = [
			"id",
			"tenant",
			"team",
			"provider",
			"api_key",
			"base_url",
			"region",
			"eu_only",
			"enabled",
			"monthly_budget_cents",
			"daily_token_limit",
			"rpm_limit",
			"tpm_limit",
			"created_at",
			"updated_at",
		]


class AIAllowedModelSerializer(serializers.ModelSerializer):
	class Meta:
		model = AIAllowedModel
		fields = ["id", "team", "model", "enabled"]


class AIPolicySerializer(serializers.ModelSerializer):
	class Meta:
		model = AIPolicy
		fields = [
			"id",
			"tenant",
			"team",
			"pii_masking_enabled",
			"anonymize_before_send",
			"chunk_size",
			"allow_external_transfer",
			"logging_opt_in",
			"created_at",
			"updated_at",
		]


class AIFeatureFlagSerializer(serializers.ModelSerializer):
	class Meta:
		model = AIFeatureFlag
		fields = ["id", "team", "name", "enabled"]


class AIUsageLogSerializer(serializers.ModelSerializer):
	class Meta:
		model = AIUsageLog
		fields = [
			"id",
			"tenant",
			"team",
			"user",
			"provider",
			"model",
			"use_case",
			"request_chars",
			"request_preview",
			"response_chars",
			"response_preview",
			"prompt_tokens",
			"completion_tokens",
			"cost_cents",
			"success",
			"status_code",
			"metadata",
			"created_at",
		]

