## Deployment (Dev/Prod)

- Dev: `docker compose up -d`; Debug aktiv, Dienste lokal erreichbar.
- Prod: Reverse Proxy (nginx/traefik) mit TLS, separate Netzwerke, Ressourcen-Limits, Daten-Backups, Observability (OTel + Prometheus/Grafana), Secrets via Vault/KMS.
- Datenhaltung: PostgreSQL mit Point-in-Time-Recovery, MinIO/S3 Versioning, OpenSearch Snapshots.
- Sicherheit: CSRF/Session-Hardening, Content Security Policy, Security Headers, regelmäßige Dependency-Updates.

