#building off of calc/contracts/management/commands
import os
import logging

import pandas as pd
import math
import datetime

from django.core.management import BaseCommand
from optparse import make_option
from django.core.management import call_command

from price_prediction.models import LaborCategoryLookUp,DecompressLaborCategory

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

def making_categories(df):
    """
    This function assumes there is a folder called data, that contains csv's with data on schedule information 
    of different positions to contract for.
    this function creates a mapping from labor categories to education level + years of experience + schedule
    """
    
    #making use of the mapping of Labor Category to higher level categorization
    categories = {
        "None":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        },
        "High School":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        },
        "Associates":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        },
        "Bachelors":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        },
        "Masters":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        },
        "Ph.D.":{
            "0-5":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "6-10":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            },
            "11-15":{
                "PES":{"freq":0,"labor categories":[]},
                "MOBIS":{"freq":0,"labor categories":[]},
                "Environmental":{"freq":0,"labor categories":[]},
                "Logistics":{"freq":0,"labor categories":[]},
                "Consolidated":{"freq":0,"labor categories":[]},
                "AIMS":{"freq":0,"labor categories":[]},
                "Language Services":{"freq":0,"labor categories":[]}
            }
        }
    }
    seen_labor_categories = []
    years_exp = ""
   
    for index in df.index:
        #this handles double counting, because about 1 out of every 100- every 1000 are double counted
        if df.ix[index]["Labor Category"] in seen_labor_categories: continue
        else:
            seen_labor_categories.append(df.ix[index]["Labor Category"])
        #This part of the code classifies the data into buckets based on some simple rules.
        if df.ix[index]["MinExpAct"] <6 or is_nan(df.ix[index]):
            years_exp = "0-5"
        elif df.ix[index]["MinExpAct"] >=6 and df.ix[index]["MinExpAct"] < 11:
            years_exp = "6-10"
        elif df.ix[index]["MinExpAct"] >= 11 and df.ix[index]["MinExpAct"] < 16:
            years_exp = "11-15"
            
        education_level = df.ix[index]["Education"] if not is_nan(df.ix[index]["Education"]) else "None" 
        categories[ education_level ][ years_exp ][ df.ix[index]["Schedule"] ]["freq"] += 1
        categories[ education_level ][ years_exp ][ df.ix[index]["Schedule"] ]["labor categories"].append(df.ix[index]["Labor Category"])
            
    return categories

def making_labor_category_to_high_level(categories):
    """
    This function assumes making_categories has been called.  
    It creates a mapping from individual labor categories to a higher level mapping which will be used in the time series analysis.
    Using this function we will create broad labor categories with enough data for a meaningful timeseries
    """
    list_of_categories = []
    labor_category_to_high_level_category = {}
    for education_level in categories.keys():
        for years_of_experience in categories[education_level].keys():
            for schedule in categories[education_level][years_of_experience].keys():
                for labor_category in categories[education_level][years_of_experience][schedule]["labor categories"]:
                    labor_category_to_high_level_category[labor_category] = education_level +"_"+ years_of_experience +"_"+ schedule
                    if education_level +"_"+ years_of_experience +"_"+ schedule not in list_of_categories:
                        list_of_categories.append(education_level +"_"+ years_of_experience +"_"+ schedule)

    return list_of_categories, labor_category_to_high_level_category


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
