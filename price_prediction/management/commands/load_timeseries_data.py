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


def find_current_option_startdate(export_date, begin_date, end_date, option_years=5):
    # Jan 4th 2017
    # =1/4/2017-(1/9/2004+5+5)
    years_of_contract = (end_date - begin_date).days/365.2425
    num_option_periods = years_of_contract // option_years
    return begin_date + relativedelta( years=int(num_option_periods*option_years) )
        

class Command(BaseCommand):

    default_filename = 'contracts/docs/hourly_prices.csv'

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
        LaborCategoryLookUp.objects.all().delete()

        filename = options['filename']
        if not filename or not os.path.exists(filename):
            raise ValueError('invalid filename')

        filepath = os.path.abspath(filename)
        df = pd.read_csv(filepath)
        log.info("Processing new datafile")
        categories = making_categories(df)
        list_of_categories, labor_category = making_labor_category_to_high_level(categories)
        set_of_time_series = {}.fromkeys(list_of_categories,pd.DataFrame())

        compressed_df = pd.DataFrame()
        compressed_df = df["Year 1/base"]
        compressed_df = df["Begin Date"]
        compressed_df = df["Labor Category"]
        
        for ind in df.index:
            labor_cat_lookup = labor_category[df.ix[ind]["Labor Category"]]
            decompress = DecompressLaborCategory(labor_category=df.ix[ind]["Labor Category"],labor_key=labor_cat_lookup)
            decompress.save()
            labor_lookup = LaborCategoryLookUp(labor_key=labor_cat_lookup,labor_value=df.ix[ind]["Year 1/base"],start_date=date_to_datetime(df.ix[ind]["Begin Date"]),labor_category=df.ix[ind]["Labor Category"])
            labor_lookup.save()
       

        log.info("End load_data task")
