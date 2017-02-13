#building off of calc/contracts/management/commands
import os
import logging

import pandas as pd
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand
from optparse import make_option
from django.core.management import call_command

from price_prediction.models import LaborCategory

#write tests for this -

# make sure each of these functions performs appropriately
# - smoke test
# - (minimal) doc tests
# - edge cases
# - check to make sure data is saved to the database

def date_to_datetime(time_string):
    return datetime.datetime.strptime(time_string, '%m/%d/%Y')

def is_nan(obj):
    if type(obj) == type(float()):
        return math.isnan(obj)
    else:
        return False
    
def money_to_float(string):
    """
    hourly wages have dollar signs and use commas, 
    this method removes those things, so we can treat stuff as floats
    """
    if type(string) == type(str()):
        string = string.replace("$","").replace(",","")
        return float(string)
    else:
        return string


def find_current_option_startdate(export_date, begin_date, option_years=5):
    years_of_contract = (export_date - begin_date).days/365.2425
    num_option_periods = years_of_contract // option_years
    return begin_date + relativedelta( years=int(num_option_periods*option_years) )
        

class Command(BaseCommand):

    default_filename = 'contracts/docs/current_labor_categories.xlsx'

    option_list = BaseCommand.option_list + (
        make_option(
            '-f', '--filename',
            default=default_filename,
            help='input filename (.csv, default {})'.format(default_filename)
        ),
    )

    def handle(self, *args, **options):
        log = logging.getLogger(__name__)

        log.info("Begin load_data task")

        log.info("Deleting existing contract records")
        LaborCategory.objects.all().delete()

        filename = options['filename']
        if not filename or not os.path.exists(filename):
            raise ValueError('invalid filename')

        filepath = os.path.abspath(filename)
        if filepath.endswith("csv"):
            df = pd.read_csv(filepath)
        elif filepath.endswith("xlsx"):
            df = pd.read_excel(filepath)
        log.info("Processing new datafile")
        
        for ind in df.index:
            current_startdate = find_current_option_startdate(
                    datetime(year=2017,
                             month=1,
                             day=4),
                    df.ix[ind]["Begin Date"],
                    option_years=5)

            current_startdate = current_startdate.to_datetime()
            labor_category_year1 = LaborCategory(
                labor_category=df.ix[ind]["Labor Category"],
                date=current_startdate,
                price=round(money_to_float(df.ix[ind]["Year 1/base"])))
            labor_category_year1.save()

            current_startdate = datetime(current_startdate.year+1,current_startdate.month,current_startdate.day)
            labor_category_year2 = LaborCategory(
                labor_category=df.ix[ind]["Labor Category"],
                date=current_startdate,
                price=round(money_to_float(df.ix[ind]["Year 2"])))
            labor_category_year2.save()

            current_startdate = datetime(current_startdate.year+1,current_startdate.month,current_startdate.day)
            labor_category_year3 = LaborCategory(
                labor_category=df.ix[ind]["Labor Category"],
                date=current_startdate,
                price=round(money_to_float(df.ix[ind]["Year 3"])))
            labor_category_year3.save()

            current_startdate = datetime(current_startdate.year+1,current_startdate.month,current_startdate.day)
            labor_category_year4 = LaborCategory(
                labor_category=df.ix[ind]["Labor Category"],
                date=current_startdate,
                price=round(money_to_float(df.ix[ind]["Year 1/base"])))
            labor_category_year4.save()

            current_startdate = datetime(current_startdate.year+1,current_startdate.month,current_startdate.day)
            labor_category_year5 = LaborCategory(
                labor_category=df.ix[ind]["Labor Category"],
                date=current_startdate,
                price=round(money_to_float(df.ix[ind]["Year 1/base"])))
            labor_category_year5.save()
