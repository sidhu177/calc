# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0010_auto_20170117_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='fittedvaluesbycategory',
            name='last_two_years_lower_bound',
            field=models.DecimalField(default=0, max_digits=200, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fittedvaluesbycategory',
            name='last_two_years_upper_bound',
            field=models.DecimalField(default=0, max_digits=200, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fittedvaluesbycategory',
            name='last_year_lower_bound',
            field=models.DecimalField(default=0, max_digits=200, decimal_places=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fittedvaluesbycategory',
            name='last_year_upper_bound',
            field=models.DecimalField(default=0, max_digits=200, decimal_places=2),
            preserve_default=False,
        ),
    ]
