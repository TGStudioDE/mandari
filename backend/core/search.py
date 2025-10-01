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
    base_index = os.getenv("OPENSEARCH_INDEX", "mandari-documents")
    tenant_id = doc.get("tenant_id")
    index_name = f"{base_index}-{tenant_id}" if tenant_id else base_index
    settings_body = {
        "settings": {
            "analysis": {
                "filter": {
                    "german_stop": {"type": "stop", "stopwords": "_german_"},
                    "german_stemmer": {"type": "stemmer", "language": "light_german"},
                    "german_lowercase": {"type": "lowercase"},
                    "german_keywords": {"type": "keyword_marker", "keywords": []},
                },
                "analyzer": {
                    "german_custom": {
                        "tokenizer": "standard",
                        "filter": ["german_lowercase", "german_stop", "german_keywords", "german_stemmer"],
                    }
                },
            },
            "index": {"knn": True},
        },
        "mappings": {
            "properties": {
                "tenant_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "german_custom"},
                "content_text": {"type": "text", "analyzer": "german_custom"},
                "committee_id": {"type": "keyword"},
                "created_at": {"type": "date"},
            }
        },
    }
    try:
        client.indices.create(index=index_name, body=settings_body)
    except Exception:
        # ignore index already exists
        pass
    client.index(index=index_name, id=doc["id"], body=doc, refresh=True)

