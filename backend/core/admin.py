from django.contrib import admin, messages

from .models import AgendaItem, Committee, Document, Meeting, Motion, Notification, OParlSource, Organization, Person, Position, ShareLink, Team, TeamMembership, Tenant, User, AIModelRegistry, AIProviderConfig, AIAllowedModel, AIPolicy, AIFeatureFlag, AIUsageLog


admin.site.register(Tenant)
admin.site.register(User)
admin.site.register(Organization)
admin.site.register(Committee)
admin.site.register(Person)
admin.site.register(Meeting)
admin.site.register(AgendaItem)
admin.site.register(Document)
admin.site.register(Motion)
admin.site.register(ShareLink)
admin.site.register(Position)
admin.site.register(Notification)
admin.site.register(Team)
admin.site.register(TeamMembership)
admin.site.register(OParlSource)
admin.site.register(AIModelRegistry)
class AIProviderConfigAdmin(admin.ModelAdmin):
	list_display = ("team", "provider", "region", "enabled")
	actions = ["test_provider_call"]

	def test_provider_call(self, request, queryset):
		from core.ai.runtime import perform_test_call
		success = 0
		for cfg in queryset:
			res = perform_test_call(cfg)
			if res.get("status", 500) < 400:
				success += 1
				messages.info(request, f"{cfg}: OK ({res.get('text','')})")
			else:
				messages.error(request, f"{cfg}: Fehler {res.get('status')} - {res.get('error')}")
		messages.success(request, f"Testaufrufe abgeschlossen. Erfolgreich: {success}/{queryset.count()}")

admin.site.register(AIProviderConfig, AIProviderConfigAdmin)
admin.site.register(AIAllowedModel)
admin.site.register(AIPolicy)
admin.site.register(AIFeatureFlag)
admin.site.register(AIUsageLog)

