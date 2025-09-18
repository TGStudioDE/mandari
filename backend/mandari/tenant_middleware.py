from __future__ import annotations

from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
	def process_request(self, request):
		# Resolve tenant by subdomain or header. Fallback: query param "tenant".
		domain = request.get_host().split(":")[0]
		req_tenant = request.headers.get("X-Tenant") or request.GET.get("tenant")
		request.tenant_hint = req_tenant or domain
		return None


