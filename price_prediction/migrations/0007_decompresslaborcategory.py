# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0006_auto_20161220_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='DecompressLaborCategory',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('labor_category', models.CharField(max_length=400)),
                ('labor_key', models.CharField(max_length=400)),
            ],
        ),
    ]
