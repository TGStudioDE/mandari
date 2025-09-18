from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Document
from .search import index_document


@receiver(post_save, sender=Document)
def on_document_saved(sender, instance: Document, created, **kwargs):
	try:
		index_document({
			"id": instance.id,
			"tenant_id": instance.tenant_id,
			"title": instance.title,
			"content_text": instance.content_text,
		})
	except Exception:
		# Swallow indexing errors to not block writes
		pass

