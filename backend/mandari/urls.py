from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponseRedirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django_prometheus import exports as prometheus_exports
from django.http import JsonResponse


def health_view(request):
	return JsonResponse({
		"status": "ok",
		"app": "mandari",
	})

def redirect_to_frontend(request):
    # Standard auf Website leiten; Admin-/Kunden-Dashboards laufen unabhängig.
    return HttpResponseRedirect("http://localhost:4321/")

urlpatterns = [
	path("", redirect_to_frontend, name="home"),
	path("admin/", admin.site.urls),
	path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
	path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
	path("api/", include("core.urls")),
	path("-/health", health_view, name="health"),
	path("-/metrics", prometheus_exports.ExportToDjangoView, name="metrics"),
]

