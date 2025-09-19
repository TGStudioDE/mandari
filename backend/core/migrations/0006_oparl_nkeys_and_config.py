from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		("core", "0005_lead"),
	]

	operations = [
		migrations.AddField(
			model_name="organization",
			name="source_base",
			field=models.CharField(default="", blank=True, max_length=255, db_index=True),
		),
		migrations.AddField(
			model_name="organization",
			name="raw",
			field=models.JSONField(default=dict),
		),
		migrations.AddField(
			model_name="committee",
			name="source_base",
			field=models.CharField(default="", blank=True, max_length=255, db_index=True),
		),
		migrations.AddField(
			model_name="committee",
			name="raw",
			field=models.JSONField(default=dict),
		),
		migrations.AddField(
			model_name="person",
			name="source_base",
			field=models.CharField(default="", blank=True, max_length=255, db_index=True),
		),
		migrations.AddField(
			model_name="person",
			name="raw",
			field=models.JSONField(default=dict),
		),
		migrations.AddField(
			model_name="meeting",
			name="source_base",
			field=models.CharField(default="", blank=True, max_length=255, db_index=True),
		),
		migrations.AddField(
			model_name="meeting",
			name="raw",
			field=models.JSONField(default=dict),
		),
		migrations.AddField(
			model_name="agendaitem",
			name="source_base",
			field=models.CharField(default="", blank=True, max_length=255, db_index=True),
		),
		migrations.AddField(
			model_name="agendaitem",
			name="raw",
			field=models.JSONField(default=dict),
		),
		migrations.AddField(
			model_name="document",
			name="source_base",
			field=models.CharField(default="", blank=True, max_length=255, db_index=True),
		),
		migrations.AddField(
			model_name="document",
			name="mimetype",
			field=models.CharField(default="", blank=True, max_length=100),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="team",
			field=models.ForeignKey(null=True, blank=True, on_delete=models.deletion.CASCADE, to="core.team"),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="auth_type",
			field=models.CharField(default="none", max_length=20, choices=[("none", "None"), ("api_key", "API Key"), ("basic", "Basic Auth")]),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="api_key_header",
			field=models.CharField(default="Authorization", blank=True, max_length=100),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="api_key_value",
			field=models.CharField(default="", blank=True, max_length=500),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="username",
			field=models.CharField(default="", blank=True, max_length=200),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="password",
			field=models.CharField(default="", blank=True, max_length=200),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="requests_per_minute",
			field=models.PositiveIntegerField(default=60),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="max_parallel_requests",
			field=models.PositiveIntegerField(default=4),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="request_timeout_seconds",
			field=models.PositiveIntegerField(default=30),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="max_retries",
			field=models.PositiveIntegerField(default=3),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="include_body",
			field=models.BooleanField(default=True),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="include_person",
			field=models.BooleanField(default=True),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="include_organization",
			field=models.BooleanField(default=True),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="include_meeting",
			field=models.BooleanField(default=True),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="include_agenda_item",
			field=models.BooleanField(default=True),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="include_paper",
			field=models.BooleanField(default=True),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="include_file",
			field=models.BooleanField(default=True),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="cron",
			field=models.CharField(default="", blank=True, max_length=100),
		),
		migrations.AddField(
			model_name="oparlsource",
			name="frequency_seconds",
			field=models.PositiveIntegerField(default=0),
		),
	]