# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0007_decompresslaborcategory'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrendByCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('labor_category', models.CharField(max_length=400)),
                ('labor_key', models.CharField(max_length=400)),
                ('trend', models.DecimalField(max_digits=200, decimal_places=2)),
                ('start_date', models.DateField()),
            ],
        ),
    ]
