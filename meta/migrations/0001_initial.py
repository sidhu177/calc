# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def insert_site(apps, schema_editor):
    print("running insert_site")
    Site = apps.get_model("sites", "Site")
    print(Site.objects.all())
    site = Site.objects.get(pk=1)
    site.domain = 'calc.gsa.gov'
    site.name = 'CALC'
    site.save()


class Migration(migrations.Migration):
    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_site)
    ]
