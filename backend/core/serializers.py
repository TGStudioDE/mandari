from rest_framework import serializers

from .models import AgendaItem, Committee, Document, Meeting, Motion, OParlSource, Organization, Person, ShareLink, Team, TeamMembership, Tenant


class TenantSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tenant
		fields = ["id", "name", "slug", "domain"]


class CommitteeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Committee
        fields = [
            "id",
            "tenant",
            "name",
            "oparl_id",
            "organization",
            "source_base",
            "raw",
        ]


class PersonSerializer(serializers.ModelSerializer):
	class Meta:
		model = Person
        fields = ["id", "tenant", "name", "party", "oparl_id", "source_base", "raw"]


class OrganizationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Organization
        fields = ["id", "tenant", "name", "oparl_id", "source_base", "raw"]


class MeetingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Meeting
        fields = [
            "id",
            "tenant",
            "committee",
            "start",
            "end",
            "oparl_id",
            "source_base",
            "raw",
        ]


class AgendaItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = AgendaItem
        fields = [
            "id",
            "tenant",
            "meeting",
            "position",
            "title",
            "category",
            "oparl_id",
            "source_base",
            "raw",
        ]


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
            "source_base",
            "mimetype",
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
        fields = [
            "id",
            "tenant",
            "team",
            "root_url",
            "enabled",
            "last_synced_at",
            "etag",
            "last_modified",
            "auth_type",
            "api_key_header",
            "api_key_value",
            "username",
            "password",
            "requests_per_minute",
            "max_parallel_requests",
            "request_timeout_seconds",
            "max_retries",
            "include_body",
            "include_person",
            "include_organization",
            "include_meeting",
            "include_agenda_item",
            "include_paper",
            "include_file",
            "cron",
            "frequency_seconds",
        ]

