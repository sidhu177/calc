# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0009_auto_20170111_1505'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fittedvaluesbycategory',
            old_name='fittedvalue',
            new_name='all_fittedvalues',
        ),
        migrations.AddField(
            model_name='fittedvaluesbycategory',
            name='last_two_years_fittedvalues',
            field=models.DecimalField(max_digits=200, decimal_places=2, default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fittedvaluesbycategory',
            name='last_year_fittedvalues',
            field=models.DecimalField(max_digits=200, decimal_places=2, default=0),
            preserve_default=False,
        ),
    ]
