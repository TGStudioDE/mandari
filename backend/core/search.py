from __future__ import annotations

import os
from typing import Any, Dict

from opensearchpy import OpenSearch


def get_client() -> OpenSearch:
	host = os.getenv("OPENSEARCH_HOST", "opensearch")
	port = int(os.getenv("OPENSEARCH_PORT", "9200"))
	return OpenSearch(
		hosts=[{"host": host, "port": port}],
		ssl_enable=False,
		verify_certs=False,
	)


def index_document(doc: Dict[str, Any]) -> None:
	client = get_client()
	index_name = os.getenv("OPENSEARCH_INDEX", "mandari-documents")
	client.indices.create(index=index_name, ignore=400, body={
		"settings": {
			"index": {
				"knn": True
			}
		},
		"mappings": {
			"properties": {
				"tenant_id": {"type": "keyword"},
				"title": {"type": "text"},
				"content_text": {"type": "text"},
			}
		}
	})
	client.index(index=index_name, id=doc["id"], body=doc, refresh=True)

