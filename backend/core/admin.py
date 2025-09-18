from django.contrib import admin

from .models import AgendaItem, Committee, Document, Meeting, Motion, Notification, Organization, Person, Position, ShareLink, Tenant, User


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

