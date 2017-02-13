# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0013_laborcategory'),
    ]

    operations = [
        migrations.CreateModel(
            name='OverallSpread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('labor_category', models.CharField(max_length=400)),
                ('year', models.DecimalField(max_digits=200, decimal_places=2)),
                ('spread', models.DecimalField(max_digits=200, decimal_places=2)),
            ],
        ),
    ]
