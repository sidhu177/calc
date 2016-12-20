# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0005_auto_20161212_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='fittedvaluesbycategory',
            name='labor_category',
            field=models.CharField(max_length=400, default=datetime.datetime(2016, 12, 20, 16, 54, 56, 391590, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='laborcategorylookup',
            name='labor_category',
            field=models.CharField(max_length=400, default=datetime.datetime(2016, 12, 20, 16, 55, 6, 629091, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pricemodels',
            name='labor_category',
            field=models.CharField(max_length=400, default='none'),
            preserve_default=False,
        ),
    ]
