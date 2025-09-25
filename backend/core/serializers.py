from rest_framework import serializers

from .models import AgendaItem, Committee, Document, Lead, Meeting, Motion, OParlSource, Organization, Person, ShareLink, Team, TeamMembership, Tenant


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

