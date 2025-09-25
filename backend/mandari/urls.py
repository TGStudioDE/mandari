from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponseRedirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def redirect_to_frontend(request):
	return HttpResponseRedirect("http://localhost:4321/")

urlpatterns = [
	path("", redirect_to_frontend, name="home"),
	path("admin/", admin.site.urls),
	path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
	path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
	path("api/", include("core.urls")),
]

