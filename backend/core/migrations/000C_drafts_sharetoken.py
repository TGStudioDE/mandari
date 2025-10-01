from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		("core", "000B_roles"),
	]

	operations = [
		migrations.CreateModel(
			name="Draft",
			fields=[
				("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("title", models.CharField(max_length=300)),
				("content", models.JSONField(blank=True, default=dict)),
				("status", models.CharField(default="draft", max_length=20)),
				("version", models.PositiveIntegerField(default=1)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("updated_at", models.DateTimeField(auto_now=True)),
				(
					"org",
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="drafts", to="core.tenant"),
				),
				(
					"owner",
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="drafts", to="core.user"),
				),
			],
		),
		migrations.CreateModel(
			name="ShareTokenLog",
			fields=[
				("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("jti", models.CharField(max_length=64, unique=True)),
				("scope", models.CharField(default="view", max_length=20)),
				("expires_at", models.DateTimeField()),
				("created_at", models.DateTimeField(auto_now_add=True)),
				(
					"draft",
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="share_tokens", to="core.draft"),
				),
				(
					"org",
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="share_tokens", to="core.tenant"),
				),
				(
					"created_by",
					models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.user"),
				),
			],
		),
	]

