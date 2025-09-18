from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

	initial = True

	dependencies = []

	operations = [
		migrations.CreateModel(
			name='Tenant',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('name', models.CharField(max_length=200)),
				('slug', models.SlugField(unique=True)),
				('domain', models.CharField(blank=True, default='', max_length=255)),
			],
		),
	]

