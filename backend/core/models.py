from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


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



# =====================
# AI Konfiguration
# =====================

class AIModelRegistry(models.Model):
	"""Globale Registry von Modellen und ihren Fähigkeiten.

	Admins können daraus teamweise zulässige Modelle wählen.
	"""

	PROVIDER_CHOICES = [
		("openai", "OpenAI"),
		("groq", "Groq"),
		("local", "Local"),
	]

	CAPABILITY_CHOICES = [
		("text", "Text Generation / Summary"),
		("embeddings", "Embeddings"),
		("rerank", "Rerank"),
		("ocr", "OCR"),
	]

	name = models.CharField(max_length=100)  # z.B. gpt-4o-mini, llama-3.1-8b
	provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
	capability = models.CharField(max_length=20, choices=CAPABILITY_CHOICES)
	max_input_tokens = models.PositiveIntegerField(default=128000)
	max_output_tokens = models.PositiveIntegerField(default=4096)
	cost_prompt_mtokens = models.PositiveIntegerField(default=0)  # Milli-Tokenpreis in Cent
	cost_completion_mtokens = models.PositiveIntegerField(default=0)
	metadata = models.JSONField(default=dict, blank=True)
	is_default = models.BooleanField(default=False)

	class Meta:
		unique_together = ("provider", "name")

	def __str__(self) -> str:
		return f"{self.provider}:{self.name} ({self.capability})"


class AIProviderConfig(models.Model):
	"""Team-spezifische Provider-Konfiguration inkl. Limits und Regionen."""

	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="ai_providers")
	provider = models.CharField(max_length=20, choices=AIModelRegistry.PROVIDER_CHOICES)
	api_key = models.CharField(max_length=256, blank=True, default="")
	base_url = models.URLField(blank=True, default="")  # kompatibel zu OpenAI-API, optional für Local/Groq
	region = models.CharField(max_length=50, blank=True, default="eu-central")
	eu_only = models.BooleanField(default=True)
	enabled = models.BooleanField(default=True)
	# Limits/Kosten
	monthly_budget_cents = models.PositiveIntegerField(default=0)  # 0=unbegrenzt
	daily_token_limit = models.PositiveIntegerField(default=0)  # 0=unbegrenzt
	rpm_limit = models.PositiveIntegerField(default=0)
	tpm_limit = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ("team", "provider")

	def __str__(self) -> str:
		return f"{self.team}::{self.provider}"


class AIAllowedModel(models.Model):
	"""Whitelist zulässiger Modelle pro Team."""

	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="ai_allowed_models")
	model = models.ForeignKey(AIModelRegistry, on_delete=models.CASCADE)
	enabled = models.BooleanField(default=True)

	class Meta:
		unique_together = ("team", "model")


class AIPolicy(models.Model):
	"""Daten- und Protokollrichtlinien pro Team."""

	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="ai_policy")
	pii_masking_enabled = models.BooleanField(default=True)
	anonymize_before_send = models.BooleanField(default=True)
	chunk_size = models.PositiveIntegerField(default=2000)
	allow_external_transfer = models.BooleanField(default=False)  # muss aktiv freigegeben sein
	logging_opt_in = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ("team", "tenant")


class AIFeatureFlag(models.Model):
	"""Feature-Flags je Team für KI-Funktionalitäten."""

	team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="ai_feature_flags")
	name = models.CharField(max_length=100)  # e.g. summarize, keywords, embeddings, rerank, diff_explain
	enabled = models.BooleanField(default=True)

	class Meta:
		unique_together = ("team", "name")

	def __str__(self) -> str:
		return f"{self.team}:{self.name}={self.enabled}"


class AIUsageLog(models.Model):
	"""Audit- und Kostenprotokoll je Request/Response."""

	tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
	team = models.ForeignKey(Team, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	provider = models.CharField(max_length=20, choices=AIModelRegistry.PROVIDER_CHOICES)
	model = models.CharField(max_length=100)
	use_case = models.CharField(max_length=50)  # summarize, keywords, embeddings, rerank, diff
	request_chars = models.PositiveIntegerField(default=0)
	request_preview = models.TextField(blank=True, default="")
	response_chars = models.PositiveIntegerField(default=0)
	response_preview = models.TextField(blank=True, default="")
	prompt_tokens = models.PositiveIntegerField(default=0)
	completion_tokens = models.PositiveIntegerField(default=0)
	cost_cents = models.PositiveIntegerField(default=0)
	success = models.BooleanField(default=True)
	status_code = models.PositiveIntegerField(default=200)
	metadata = models.JSONField(default=dict, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		indexes = [
			models.Index(fields=["team", "created_at"]),
			models.Index(fields=["tenant", "created_at"]),
		]
