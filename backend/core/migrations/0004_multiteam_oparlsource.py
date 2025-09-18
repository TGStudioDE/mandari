from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		("core", "0003_user_groups_perms"),
	]

	operations = [
		migrations.CreateModel(
			name="Team",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("name", models.CharField(max_length=200)),
				("slug", models.SlugField()),
				("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
			options={"unique_together": {("tenant", "slug")}},
		),
		migrations.CreateModel(
			name="TeamMembership",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("role", models.CharField(default="member", max_length=50)),
				("team", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="core.team")),
				("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="team_memberships", to="core.user")),
			],
			options={"unique_together": {("team", "user")}},
		),
		migrations.CreateModel(
			name="OParlSource",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("root_url", models.URLField()),
				("enabled", models.BooleanField(default=True)),
				("last_synced_at", models.DateTimeField(blank=True, null=True)),
				("etag", models.CharField(blank=True, default="", max_length=128)),
				("last_modified", models.CharField(blank=True, default="", max_length=128)),
				("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
			options={"unique_together": {("tenant", "root_url")}},
		),
	]


