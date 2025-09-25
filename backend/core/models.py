from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class Tenant(models.Model):
	name = models.CharField(max_length=200)
	slug = models.SlugField(unique=True)
	domain = models.CharField(max_length=255, blank=True, default="")

	def __str__(self) -> str:
		return self.name


class User(AbstractUser):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
	role = models.CharField(
		max_length=50,
		choices=[
			("member", "Member"),
			("faction_admin", "Faction Admin"),
			("guest", "Guest"),
			("staff", "Staff"),
		],
		default="member",
	)


class Team(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	slug = models.SlugField()

	class Meta:
		unique_together = ("tenant", "slug")

	def __str__(self) -> str:
		return f"{self.tenant.slug}:{self.slug}"


class TeamMembership(models.Model):
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_memberships")
	role = models.CharField(max_length=50, default="member")

	class Meta:
		unique_together = ("team", "user")


class Organization(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	oparl_id = models.CharField(max_length=255, blank=True, default="")

	def __str__(self) -> str:
		return self.name


class Committee(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	oparl_id = models.CharField(max_length=255, blank=True, default="")
	organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self) -> str:
		return self.name


class Person(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	party = models.CharField(max_length=255, blank=True, default="")
	oparl_id = models.CharField(max_length=255, blank=True, default="")

	def __str__(self) -> str:
		return self.name


class Meeting(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
	start = models.DateTimeField()
	end = models.DateTimeField(null=True, blank=True)
	oparl_id = models.CharField(max_length=255, blank=True, default="")


class AgendaItem(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="agenda_items")
	position = models.PositiveIntegerField()
	title = models.CharField(max_length=500)
	category = models.CharField(max_length=100, blank=True, default="")
	oparl_id = models.CharField(max_length=255, blank=True, default="")

	class Meta:
		unique_together = ("meeting", "position")
		ordering = ["position"]


class Document(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	agenda_item = models.ForeignKey(AgendaItem, on_delete=models.SET_NULL, null=True, blank=True)
	title = models.CharField(max_length=500)
	file = models.FileField(upload_to="documents/", null=True, blank=True)
	raw = models.JSONField(default=dict)
	normalized = models.JSONField(default=dict)
	content_text = models.TextField(blank=True, default="")
	content_hash = models.CharField(max_length=64, db_index=True)
	oparl_id = models.CharField(max_length=255, blank=True, default="")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class Motion(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	title = models.CharField(max_length=500)
	status = models.CharField(
		max_length=30,
		choices=[
			("draft", "Draft"),
			("review", "Fraction Review"),
			("final", "Final"),
			("submitted", "Submitted"),
		],
		default="draft",
	)
	content = models.JSONField(default=dict)  # CRDT/Yjs JSON snapshot placeholder
	version = models.PositiveIntegerField(default=1)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class ShareLink(models.Model):
	motion = models.ForeignKey(Motion, on_delete=models.CASCADE, related_name="share_links")
	token = models.CharField(max_length=64, unique=True)
	expires_at = models.DateTimeField(null=True, blank=True)
	can_edit = models.BooleanField(default=False)


class Position(models.Model):
	motion = models.ForeignKey(Motion, on_delete=models.CASCADE, related_name="positions")
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	value = models.CharField(max_length=50)  # e.g., support/oppose/neutral


class Notification(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	channel = models.CharField(max_length=30)  # email, webpush, matrix
	payload = models.JSONField(default=dict)
	is_sent = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)


class OParlSource(models.Model):
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	root_url = models.URLField()
	enabled = models.BooleanField(default=True)
	last_synced_at = models.DateTimeField(null=True, blank=True)
	etag = models.CharField(max_length=128, blank=True, default="")
	last_modified = models.CharField(max_length=128, blank=True, default="")

	class Meta:
		unique_together = ("tenant", "root_url")


class Lead(models.Model):
	"""Lead-Eintrag für Website-Kontakt mit Double-Opt-In."""
	tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)
	company = models.CharField(max_length=255, blank=True, default="")
	name = models.CharField(max_length=255)
	email = models.EmailField(db_index=True)
	message = models.TextField(blank=True, default="")
	consent_privacy = models.BooleanField(default=False)
	consent_marketing = models.BooleanField(default=False)
	confirm_token = models.CharField(max_length=64, unique=True, default="", blank=True)
	confirmed_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if not self.confirm_token:
			self.confirm_token = uuid.uuid4().hex
		return super().save(*args, **kwargs)

	@property
	def is_confirmed(self) -> bool:
		return self.confirmed_at is not None


class RoleAssignment(models.Model):
	"""Verknüpft Benutzerrollen zu Gremien innerhalb eines Mandanten.

	Beispiele für Rollen: "sachkundig", "ratsherr", "bezirksvertretung".
	"""
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="role_assignments")
	committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name="role_assignments")
	role = models.CharField(max_length=100)

	class Meta:
		unique_together = ("tenant", "user", "committee", "role")

	def __str__(self) -> str:
		return f"{self.tenant_id}:{self.user_id}:{self.committee_id}:{self.role}"

