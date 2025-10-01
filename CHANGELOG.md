# Changelog

## 0.1.1 – STEP 0 Baseline & Guards

- BaseOrgScopeMixin eingeführt, alle Tenant-Ressourcen automatisch org-gescoped
- OpenSearch Index-Prefix pro Tenant mit German Analyzer und Completion
- Health `/-/health` und Metrics `/-/metrics` Endpoints
- Request-ID Middleware, Security-Header-Härtung, DRF Rate Limits
- Tests für Health/Request-ID und Org-Scoping (Schreiben) ergänzt