from django.core.management.base import BaseCommand
from core.models import Plan


DEFAULT_PLANS = [
	{
		"code": "free",
		"name": "Free",
		"features_json": {"public_portal": False},
		"hard_limits_json": {},
		"soft_limits_json": {},
	},
	{
		"code": "basic",
		"name": "Basic",
		"features_json": {"public_portal": True},
		"hard_limits_json": {},
		"soft_limits_json": {},
	},
	{
		"code": "pro",
		"name": "Pro",
		"features_json": {"public_portal": True, "signing": True, "ai_assist": True},
		"hard_limits_json": {},
		"soft_limits_json": {},
	},
]


class Command(BaseCommand):
	help = "Seed default subscription plans"

	def handle(self, *args, **options):
		created = 0
		for item in DEFAULT_PLANS:
			obj, was_created = Plan.objects.update_or_create(
				code=item["code"],
				defaults={
					"name": item["name"],
					"features_json": item["features_json"],
					"hard_limits_json": item["hard_limits_json"],
					"soft_limits_json": item["soft_limits_json"],
				},
			)
			created += 1 if was_created else 0
		self.stdout.write(self.style.SUCCESS(f"Seeded {len(DEFAULT_PLANS)} plans ({created} new)."))


