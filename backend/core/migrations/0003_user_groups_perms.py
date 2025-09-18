from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		("auth", "0012_alter_user_first_name_max_length"),
		("core", "0002_domain_models"),
	]

	operations = [
		migrations.AddField(
			model_name="user",
			name="groups",
			field=models.ManyToManyField(blank=True, help_text="The groups this user belongs to.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups"),
		),
		migrations.AddField(
			model_name="user",
			name="user_permissions",
			field=models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions"),
		),
	]

