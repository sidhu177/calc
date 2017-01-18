# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('price_prediction', '0011_auto_20170117_1826'),
    ]

    operations = [
        migrations.CreateModel(
            name='OneYearFitted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('labor_category', models.CharField(max_length=400)),
                ('labor_key', models.CharField(max_length=400)),
                ('upper_bound', models.DecimalField(decimal_places=2, max_digits=200)),
                ('fittedvalues', models.DecimalField(decimal_places=2, max_digits=200)),
                ('lower_bound', models.DecimalField(decimal_places=2, max_digits=200)),
                ('start_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='TwoYearsFitted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('labor_category', models.CharField(max_length=400)),
                ('labor_key', models.CharField(max_length=400)),
                ('upper_bound', models.DecimalField(decimal_places=2, max_digits=200)),
                ('fittedvalues', models.DecimalField(decimal_places=2, max_digits=200)),
                ('lower_bound', models.DecimalField(decimal_places=2, max_digits=200)),
                ('start_date', models.DateField()),
            ],
        ),
        migrations.RenameField(
            model_name='fittedvaluesbycategory',
            old_name='all_fittedvalues',
            new_name='fittedvalues',
        ),
        migrations.RemoveField(
            model_name='fittedvaluesbycategory',
            name='last_two_years_fittedvalues',
        ),
        migrations.RemoveField(
            model_name='fittedvaluesbycategory',
            name='last_two_years_lower_bound',
        ),
        migrations.RemoveField(
            model_name='fittedvaluesbycategory',
            name='last_two_years_upper_bound',
        ),
        migrations.RemoveField(
            model_name='fittedvaluesbycategory',
            name='last_year_fittedvalues',
        ),
        migrations.RemoveField(
            model_name='fittedvaluesbycategory',
            name='last_year_lower_bound',
        ),
        migrations.RemoveField(
            model_name='fittedvaluesbycategory',
            name='last_year_upper_bound',
        ),
    ]
