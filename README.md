## Frontends (SaaS Dashboards)

Dieses Repo enthält zusätzlich zu `website/` zwei eigenständige Frontends, die nicht im Website-Container laufen:

- `frontends/admin`: System-Admin-Dashboard
- `frontends/dashboard`: Kunden-Dashboard

Beide Frontends laufen separat (Vite, React, TS) und sprechen per Cookie-Auth mit dem Django-Backend (`/api`). Multi-Tenancy erfolgt per `X-Tenant` Header oder `?tenant=` Query.

Start (Dev):

1. `docker compose up -d backend postgres memcached opensearch rabbitmq minio create-bucket`
2. In separaten Terminals je Frontend:

   - Admin: `docker compose up admin-frontend`
   - Kunden: `docker compose up dashboard-frontend`

Konfiguration (Umgebung):

- Backend setzt `CORS_ALLOWED_ORIGINS` und `CSRF_TRUSTED_ORIGINS` bereits für die Ports 5173/5174.
- Frontends nutzen `VITE_API_BASE=http://localhost:8000`.

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

## MVP Closeout Progress

Version 0.1.1

- STEP 0
  - Org-Scoping zentral via `BaseOrgScopeMixin` (JWT/Session/Header)
  - OpenSearch Index-Prefix pro Org (german analyzer, completion field)
  - Health `/-/health` und Metrics `/-/metrics` (Prometheus)
  - Request-ID Middleware, Security-Header, DRF Rate Limits

