from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		("core", "0004_multiteam_oparlsource"),
	]

	operations = [
		migrations.CreateModel(
			name="Lead",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("company", models.CharField(blank=True, default="", max_length=255)),
				("name", models.CharField(max_length=255)),
				("email", models.EmailField(db_index=True, max_length=254)),
				("message", models.TextField(blank=True, default="")),
				("consent_privacy", models.BooleanField(default=False)),
				("consent_marketing", models.BooleanField(default=False)),
				("confirm_token", models.CharField(blank=True, default="", max_length=64, unique=True)),
				("confirmed_at", models.DateTimeField(blank=True, null=True)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("updated_at", models.DateTimeField(auto_now=True)),
				(
					"tenant",
					models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.tenant"),
				),
			],
		),
	]

