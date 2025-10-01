from __future__ import annotations

from typing import Optional

from django.http import Http404
from django.utils.functional import cached_property
from rest_framework import exceptions

from .models import Tenant


class BaseOrgScopeMixin:

	org_scope_field: Optional[str] = None

	@cached_property
	def _resolved_org_id(self) -> Optional[int]:
		request = getattr(self, "request", None)
		if not request:
			return None
		# 1) JWT-Claim (wird in STEP 1 implementiert) – hier defensiv lesen
		claim_org_id = None
		try:
			auth = getattr(request, "auth", None) or {}
			claim_org_id = getattr(auth, "get", lambda *_: None)("org_id") if hasattr(auth, "get") else None
		except Exception:
			claim_org_id = None
		if claim_org_id:
			return int(claim_org_id)
		# 2) Session-User
		user = getattr(request, "user", None)
		if user and getattr(user, "is_authenticated", False) and getattr(user, "tenant_id", None):
			return int(user.tenant_id)
		# 3) Middleware-Hinweis (Header X-Tenant / Host / ?tenant=)
		hint = getattr(request, "tenant_hint", None)
		if hint:
			tenant = Tenant.objects.filter(domain=hint).first() or Tenant.objects.filter(slug=hint).first()
			if tenant:
				return int(tenant.id)
		return None

	def _ensure_org_required(self) -> int:
		org_id = self._resolved_org_id
		if org_id is None:
			raise exceptions.PermissionDenied("Org-Scope erforderlich")
		return org_id

	def _detect_scope_field(self):
		if self.org_scope_field:
			return self.org_scope_field
		# Automatische Erkennung anhand des Modells
		model = getattr(getattr(self, "queryset", None), "model", None)
		if not model:
			return None
		field_names = {f.name for f in model._meta.get_fields()}
		if "tenant" in field_names:
			return "tenant_id"
		if "org" in field_names:
			return "org_id"
		return None

	def initial(self, request, *args, **kwargs):
		# Setze org_id am Request für nachgelagerte Nutzung (Logging, Search, etc.)
		request.org_id = self._resolved_org_id
		return super().initial(request, *args, **kwargs)

	def get_queryset(self):
		qs = super().get_queryset()
		scope_field = self._detect_scope_field()
		# Bei unsafe Methoden ist Org verpflichtend
		if self.request.method not in ("GET", "HEAD", "OPTIONS"):
			org_id = self._ensure_org_required()
			if scope_field:
				return qs.filter(**{scope_field: org_id})
			return qs
		# Bei safe Methods: wenn Org verfügbar, filtern; sonst (z.B. Public OParl) nicht
		org_id = self._resolved_org_id
		if scope_field and org_id is not None:
			qs = qs.filter(**{scope_field: org_id})
		return qs

	def perform_create(self, serializer):
		org_id = self._ensure_org_required()
		scope_field = self._detect_scope_field()
		if scope_field == "tenant_id":
			serializer.save(tenant_id=org_id)
			return
		if scope_field == "org_id":
			serializer.save(org_id=org_id)
			return
		# Fallback: ohne bekanntes Feld -> normal speichern
		serializer.save()

