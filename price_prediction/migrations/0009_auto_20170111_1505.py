# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0008_trendbycategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='fittedvaluesbycategory',
            name='lower_bound',
            field=models.DecimalField(default=0, max_digits=200, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fittedvaluesbycategory',
            name='upper_bound',
            field=models.DecimalField(default=0, max_digits=200, decimal_places=2),
            preserve_default=False,
        ),
    ]
