from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RoleAssignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(max_length=100)),
                ("committee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="role_assignments", to="core.committee")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.tenant")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="role_assignments", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "unique_together": {("tenant", "user", "committee", "role")},
            },
        ),
    ]

