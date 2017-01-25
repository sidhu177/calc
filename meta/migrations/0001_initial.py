# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from ._util_0001 import insert_site


class Migration(migrations.Migration):
    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_site)
    ]
