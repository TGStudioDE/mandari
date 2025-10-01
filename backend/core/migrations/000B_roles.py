from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		("core", "000A_oauthclient"),
	]

	operations = [
		migrations.CreateModel(
			name="Role",
			fields=[
				("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("slug", models.SlugField()),
				("name", models.CharField(max_length=100)),
				("description", models.TextField(blank=True, default="")),
				("permissions", models.JSONField(blank=True, default=list)),
				(
					"org",
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="roles", to="core.tenant"),
				),
			],
		),
		migrations.AlterUniqueTogether(
			name="role",
			unique_together={("org", "slug")},
		),
		migrations.CreateModel(
			name="UserRole",
			fields=[
				("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				(
					"org",
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_roles", to="core.tenant"),
				),
				(
					"user",
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_roles", to="core.user"),
				),
				(
					"role",
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_roles", to="core.role"),
				),
			],
		),
		migrations.AlterUniqueTogether(
			name="userrole",
			unique_together={("org", "user", "role")},
		),
	]

