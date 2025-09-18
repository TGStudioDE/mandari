import json
from django.urls import reverse
from rest_framework.test import APIClient
import pytest


@pytest.mark.django_db
def test_document_create_idempotent(admin_client, django_user_model):
	# create tenant
	from core.models import Tenant
	tenant = Tenant.objects.create(name="t", slug="t")

	client = APIClient()
	client.force_authenticate(user=admin_client.handler._force_user)
	data = {
		"tenant": tenant.id,
		"title": "Doc",
		"content_text": "hello",
		"content_hash": "abc123",
	}
	url = "/api/documents/"
	res1 = client.post(url, data, format="json")
	assert res1.status_code in (200, 201)
	res2 = client.post(url, data, format="json")
	assert res2.status_code == 200
	assert res1.json()["id"] == res2.json()["id"]


