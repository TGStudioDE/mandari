Mandari – Ratsarbeitssystem

Ziel
Mandari modernisiert kommunalpolitische Arbeit mit OParl-Ingest, smartem Dokumenten-/Antragsmanagement, Suche (OpenSearch) und Kollaborations-Features.

Komponenten
- Backend: Django + DRF (User, Rollen, Workflows, API)
- Ingest: FastAPI (OParl-Import, Delta-Updates, Content-Hashes)
- KI: FastAPI (Summaries, DSGVO-konform)
- Daten: PostgreSQL, S3/MinIO (Dateien), OpenSearch, RabbitMQ/Redis Streams, Memcached
- Frontend: Web-App (später)

Schnellstart
1. .env anlegen (siehe .env.example)
2. docker compose up -d
3. make migrate && make createsuperuser

Wichtige Makefile-Targets
- make up / make down / make logs
- make migrate / make django-shell
- make openapi

Ordnerstruktur
- backend/ – Django Projekt
- services/ingest/ – FastAPI OParl-Ingest
- services/ai/ – FastAPI KI-Services
- docs/ – Architektur, ERD, OpenAPI, Deployment

Sicherheit & DSGVO
- Mandantenfähigkeit, Verschlüsselung in Transit/At-Rest (Datenbanken/Buckets)
- Datenminimierung, Audit-Logs, Löschkonzepte
- KI-Aufrufe mit PII-Filter/Anonymisierung und Chunking

# mandari

