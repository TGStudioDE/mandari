from __future__ import annotations

import os
from typing import Any, Dict, Optional

from opensearchpy import OpenSearch


def get_client() -> OpenSearch:
	host = os.getenv("OPENSEARCH_HOST", "opensearch")
	port = int(os.getenv("OPENSEARCH_PORT", "9200"))
	return OpenSearch(
		hosts=[{"host": host, "port": port}],
		ssl_enable=False,
		verify_certs=False,
	)


def _org_index_name(base: str, org_id: Optional[int]) -> str:
    if org_id is None:
        return base
    return f"{org_id}-{base}"


def index_document(doc: Dict[str, Any]) -> None:
	client = get_client()
	base_index = os.getenv("OPENSEARCH_INDEX", "mandari-documents")
	org_id = doc.get("tenant_id") or doc.get("org_id")
	index_name = _org_index_name(base_index, org_id)
	client.indices.create(index=index_name, ignore=400, body={
		"settings": {
			"index": {
				"knn": True,
				"analysis": {
					"analyzer": {
						"german_custom": {
							"type": "german"
						}
					}
				}
			}
		},
		"mappings": {
			"properties": {
				"tenant_id": {"type": "keyword"},
				"title": {"type": "text", "analyzer": "german_custom"},
				"content_text": {"type": "text", "analyzer": "german_custom"},
				"title_suggest": {"type": "completion"},
			}
		}
	})
	client.index(index=index_name, id=doc["id"], body=doc, refresh=True)

