from __future__ import annotations

import json
import pytest
from django.urls import reverse
from django.test import Client
from core.models import Tenant, User, Document


@pytest.mark.django_db
def test_health_endpoint():
	c = Client()
	r = c.get("/-/health")
	assert r.status_code == 200
	data = r.json()
	assert data.get("status") == "ok"


@pytest.mark.django_db
def test_request_id_header():
	c = Client()
	r = c.get("/-/health", HTTP_X_REQUEST_ID="abc123")
	assert r.status_code == 200
	assert r["X-Request-ID"] == "abc123"


@pytest.mark.django_db
def test_org_scoping_mixin_filters_by_tenant_on_write():
	tenant = Tenant.objects.create(name="Test", slug="test")
	user = User.objects.create_user(username="u", password="p", tenant=tenant)
	c = Client()
	assert c.login(username="u", password="p")
	# create Document without explicit tenant/org in payload -> should be assigned
	r = c.post(reverse("document-list"), {"title": "T", "content_hash": "h1"})
	assert r.status_code in (201, 200)
	doc_id = r.json()["id"]
	doc = Document.objects.get(id=doc_id)
	assert doc.tenant_id == tenant.id


@pytest.mark.django_db
def test_org_scoping_safe_method_without_org_allows_public():
	c = Client()
	r = c.get(reverse("oparl-bodies"))
	# OParl may 404 if not enabled; but request should not be forbidden due to missing org
	assert r.status_code in (200, 404)

