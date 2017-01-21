# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0012_auto_20170118_1254'),
    ]

    operations = [
        migrations.CreateModel(
            name='LaborCategory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('labor_category', models.CharField(max_length=400)),
                ('date', models.DateField()),
                ('price', models.DecimalField(max_digits=200, decimal_places=2)),
            ],
        ),
    ]
