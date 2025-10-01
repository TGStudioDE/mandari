from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		("core", "0009_offerdraft_staffprofile"),
	]

	operations = [
		migrations.CreateModel(
			name="OAuthClient",
			fields=[
				("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("name", models.CharField(max_length=100)),
				("client_id", models.CharField(max_length=64, unique=True)),
				("client_secret_hashed", models.CharField(max_length=128)),
				("scopes", models.JSONField(blank=True, default=list)),
				("is_active", models.BooleanField(default=True)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("last_used_at", models.DateTimeField(blank=True, null=True)),
				(
					"org",
					models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="oauth_clients", to="core.tenant"),
				),
			],
		),
	]

