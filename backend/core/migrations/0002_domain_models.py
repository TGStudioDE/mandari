from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		("core", "0001_initial"),
	]

	operations = [
		migrations.CreateModel(
			name="User",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("password", models.CharField(max_length=128, verbose_name="password")),
				("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
				("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
				("username", models.CharField(error_messages={"unique": "A user with that username already exists."}, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.", max_length=150, unique=True, verbose_name="username")),
				("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
				("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
				("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
				("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
				("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
				("date_joined", models.DateTimeField(auto_now_add=True)),
				("role", models.CharField(choices=[("member", "Member"), ("faction_admin", "Faction Admin"), ("guest", "Guest"), ("staff", "Staff")], default="member", max_length=50)),
				("tenant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
		),
		migrations.CreateModel(
			name="Organization",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("name", models.CharField(max_length=255)),
				("oparl_id", models.CharField(blank=True, default="", max_length=255)),
				("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
		),
		migrations.CreateModel(
			name="Committee",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("name", models.CharField(max_length=255)),
				("oparl_id", models.CharField(blank=True, default="", max_length=255)),
				("organization", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.organization")),
				("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
		),
		migrations.CreateModel(
			name="Person",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("name", models.CharField(max_length=255)),
				("party", models.CharField(blank=True, default="", max_length=255)),
				("oparl_id", models.CharField(blank=True, default="", max_length=255)),
				("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
		),
		migrations.CreateModel(
			name="Meeting",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("start", models.DateTimeField()),
				("end", models.DateTimeField(blank=True, null=True)),
				("oparl_id", models.CharField(blank=True, default="", max_length=255)),
				("committee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.committee")),
				("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
		),
		migrations.CreateModel(
			name="AgendaItem",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("position", models.PositiveIntegerField()),
				("title", models.CharField(max_length=500)),
				("category", models.CharField(blank=True, default="", max_length=100)),
				("oparl_id", models.CharField(blank=True, default="", max_length=255)),
				("meeting", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="agenda_items", to="core.meeting")),
				("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
			options={"ordering": ["position"], "unique_together": {("meeting", "position")}},
		),
		migrations.CreateModel(
			name="Document",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("title", models.CharField(max_length=500)),
				("file", models.FileField(blank=True, null=True, upload_to="documents/")),
				("raw", models.JSONField(default=dict)),
				("normalized", models.JSONField(default=dict)),
				("content_text", models.TextField(blank=True, default="")),
				("content_hash", models.CharField(db_index=True, max_length=64)),
				("oparl_id", models.CharField(blank=True, default="", max_length=255)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("updated_at", models.DateTimeField(auto_now=True)),
				("agenda_item", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.agendaitem")),
				("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
		),
		migrations.CreateModel(
			name="Motion",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("title", models.CharField(max_length=500)),
				("status", models.CharField(choices=[("draft", "Draft"), ("review", "Fraction Review"), ("final", "Final"), ("submitted", "Submitted")], default="draft", max_length=30)),
				("content", models.JSONField(default=dict)),
				("version", models.PositiveIntegerField(default=1)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("updated_at", models.DateTimeField(auto_now=True)),
				("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
				("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
		),
		migrations.CreateModel(
			name="ShareLink",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("token", models.CharField(max_length=64, unique=True)),
				("expires_at", models.DateTimeField(blank=True, null=True)),
				("can_edit", models.BooleanField(default=False)),
				("motion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="share_links", to="core.motion")),
			],
		),
		migrations.CreateModel(
			name="Position",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("value", models.CharField(max_length=50)),
				("motion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="positions", to="core.motion")),
				("person", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.person")),
			],
		),
		migrations.CreateModel(
			name="Notification",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("channel", models.CharField(max_length=30)),
				("payload", models.JSONField(default=dict)),
				("is_sent", models.BooleanField(default=False)),
				("created_at", models.DateTimeField(auto_now_add=True)),
				("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
				("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
			],
		),
	]

