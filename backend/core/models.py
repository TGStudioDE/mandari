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
	# Betriebsstatus / Region
	is_active = models.BooleanField(default=True)
	region = models.CharField(max_length=50, blank=True, default="")
	# Security Policy
	mfa_required_for_admins = models.BooleanField(default=False)
	# Branding
	logo_url = models.URLField(blank=True, default="")
	color_primary = models.CharField(max_length=20, blank=True, default="#0a75ff")
	color_secondary = models.CharField(max_length=20, blank=True, default="#0f172a")

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
	# MFA
	mfa_enabled = models.BooleanField(default=False)
	mfa_secret = models.CharField(max_length=64, blank=True, default="")
	mfa_recovery_codes = models.JSONField(default=list, blank=True)
	mfa_last_verified_at = models.DateTimeField(null=True, blank=True)


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


class PasswordResetToken(models.Model):
	"""Token für Passwort-Zurücksetzen via E-Mail."""
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_reset_tokens")
	token = models.CharField(max_length=64, unique=True)
	expires_at = models.DateTimeField()
	used_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		if not self.token:
			self.token = uuid.uuid4().hex
		return super().save(*args, **kwargs)

	@property
	def is_valid(self) -> bool:
		return self.used_at is None and timezone.now() < self.expires_at


# ==========================
# Admin-/SaaS-Kernmodelle
# ==========================

class Subspace(models.Model):
	"""Isolierter Fach-/Parteiraum innerhalb eines Mandanten mit eigener URL.

	Wichtig: Subspaces sind KEINE Unterteams. Auth kann künftig separat erfolgen.
	"""
	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="subspaces")
	name = models.CharField(max_length=200)
	key = models.SlugField()
	type = models.CharField(max_length=50, blank=True, default="")
	domain = models.CharField(max_length=255, blank=True, default="")
	settings_json = models.JSONField(default=dict, blank=True)

	class Meta:
		unique_together = ("tenant", "key")

	def __str__(self) -> str:
		return f"{self.tenant.slug}:{self.key}"


class SpaceMembership(models.Model):
	"""Rollenmitgliedschaft eines Users in einem Subspace (RBAC/ABAC-Basis)."""
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="space_memberships")
	subspace = models.ForeignKey(Subspace, on_delete=models.CASCADE, related_name="memberships")
	role = models.CharField(max_length=50, default="member")  # space_admin, editor, submitter, reader

	class Meta:
		unique_together = ("user", "subspace")


class Plan(models.Model):
	code = models.SlugField(unique=True)
	name = models.CharField(max_length=100)
	features_json = models.JSONField(default=dict, blank=True)
	hard_limits_json = models.JSONField(default=dict, blank=True)
	soft_limits_json = models.JSONField(default=dict, blank=True)

	def __str__(self) -> str:
		return self.name


class Subscription(models.Model):
	org = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="subscription")
	plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
	status = models.CharField(max_length=30, default="active")  # active, past_due, canceled
	period_start = models.DateTimeField()
	period_end = models.DateTimeField()
	billing_account_id = models.CharField(max_length=100, blank=True, default="")

	def __str__(self) -> str:
		return f"{self.org.slug}:{self.plan.code}:{self.status}"


class UsageMeter(models.Model):
	org = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="usage_meters")
	metric = models.CharField(max_length=50)
	window_start = models.DateTimeField()
	window_end = models.DateTimeField()
	value = models.BigIntegerField(default=0)

	class Meta:
		index_together = (("org", "metric", "window_start", "window_end"),)


class FeatureFlag(models.Model):
	org = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="feature_flags")
	subspace = models.ForeignKey(Subspace, on_delete=models.CASCADE, null=True, blank=True, related_name="feature_flags")
	key = models.CharField(max_length=100)
	enabled = models.BooleanField(default=False)

	class Meta:
		unique_together = ("org", "subspace", "key")


class Note(models.Model):
	org = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="notes")
	subspace = models.ForeignKey(Subspace, on_delete=models.SET_NULL, null=True, blank=True, related_name="notes")
	title = models.CharField(max_length=255)
	body = models.TextField(blank=True, default="")
	tags = models.JSONField(default=list, blank=True)
	related_entity = models.CharField(max_length=100, blank=True, default="")
	visibility = models.CharField(max_length=20, default="internal")  # internal, private, public
	status = models.CharField(max_length=20, default="open")  # open, in_progress, done
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class WorkflowConfig(models.Model):
	org = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="workflow_configs")
	subspace = models.ForeignKey(Subspace, on_delete=models.SET_NULL, null=True, blank=True, related_name="workflow_configs")
	rules_json = models.JSONField(default=dict, blank=True)


class AuditLog(models.Model):
	org = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="audit_logs")
	actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	action = models.CharField(max_length=100)
	target_type = models.CharField(max_length=100, blank=True, default="")
	target_id = models.CharField(max_length=100, blank=True, default="")
	diff_json = models.JSONField(default=dict, blank=True)
	at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-at"]


class WebhookEndpoint(models.Model):
	org = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="webhook_endpoints")
	url = models.URLField()
	secret = models.CharField(max_length=128)
	events = models.JSONField(default=list, blank=True)
	enabled = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)


class ApiKey(models.Model):
	org = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="api_keys")
	name = models.CharField(max_length=100)
	scopes = models.JSONField(default=list, blank=True)
	hashed_key = models.CharField(max_length=128, unique=True)
	expires_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	last_used_at = models.DateTimeField(null=True, blank=True)

	def set_plain_key(self, plain_key: str):
		import hashlib
		self.hashed_key = hashlib.sha256(plain_key.encode("utf-8")).hexdigest()

	def check_key(self, plain_key: str) -> bool:
		import hashlib
		return self.hashed_key == hashlib.sha256(plain_key.encode("utf-8")).hexdigest()


class PricingAgreement(models.Model):
	"""Preisvereinbarung pro Mandant (Stadt) oder optional pro Subspace (Fraktion)."""
	org = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="pricing_agreements")
	subspace = models.ForeignKey('Subspace', on_delete=models.CASCADE, null=True, blank=True, related_name="pricing_agreements")
	amount_cents = models.PositiveIntegerField()
	currency = models.CharField(max_length=3, default="EUR")
	period = models.CharField(max_length=20, default="monthly")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ("org", "subspace", "currency", "period")


class Membership(models.Model):
	"""Mitgliedschaft eines Users auf Organisations-Ebene (mandantenweit)."""
	org = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="org_memberships")
	role = models.CharField(max_length=50, default="member")  # owner, billing_admin, org_admin, auditor

	class Meta:
		unique_together = ("org", "user")


class Invitation(models.Model):
	"""Einladung in eine Organisation mit optionalen Space-Rollen."""
	org = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="invitations")
	email = models.EmailField()
	role = models.CharField(max_length=50, default="member")
	subspace_roles = models.JSONField(default=list, blank=True)  # [{subspace_id, role}]
	token = models.CharField(max_length=64, unique=True, default="")
	expires_at = models.DateTimeField()
	accepted_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		if not self.token:
			self.token = uuid.uuid4().hex
		return super().save(*args, **kwargs)


class StaffProfile(models.Model):
	"""Interne Mitarbeiterprofile (Admin, Vertrieb, Support, Engineering) mit Scopes."""
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_profile")
	department = models.CharField(max_length=30, default="sales")  # admin, sales, support, engineering
	scopes = models.JSONField(default=list, blank=True)
	can_create_test_env = models.BooleanField(default=True)


class OfferDraft(models.Model):
	"""Angebotsentwurf, optional Mandant zugeordnet."""
	org = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True, related_name="offer_drafts")
	lead = models.ForeignKey('Lead', on_delete=models.SET_NULL, null=True, blank=True, related_name="offer_drafts")
	title = models.CharField(max_length=200)
	body = models.TextField(blank=True, default="")
	customer_email = models.EmailField(blank=True, default="")
	amount_cents = models.PositiveIntegerField(null=True, blank=True)
	status = models.CharField(max_length=20, default="draft")  # draft, sent, accepted, rejected, lost
	next_step = models.CharField(max_length=100, blank=True, default="")
	due_date = models.DateField(null=True, blank=True)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)