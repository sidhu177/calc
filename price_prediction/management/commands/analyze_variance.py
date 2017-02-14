#building off of calc/contracts/management/commands
import os
import logging
import asyncio
import pandas as pd
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand
from optparse import make_option
from django.core.management import call_command
import statistics as st
import numpy as np
from price_prediction.models import LaborCategory, OverallSpread
import shutil
from scipy import stats


#write tests for this -

# make sure each of these functions performs appropriately
# - smoke test
# - (minimal) doc tests
# - edge cases
# - check to make sure data is saved to the database

def is_nan(obj):
    if type(obj) == type(float()):
        return math.isnan(obj)
    else:
        return False


def count_outliers(data):
    outliers_num = 0
    mean = st.mean(data)
    stdev = st.stdev(data)
    for elem in data:
        if (elem > mean + (2*stdev)) or (elem < mean - (2*stdev)):
            outliers_num += 1
    return outliers_num

def first_quartile(List):
    if len(List) >= 4:
        List.sort()
        if len(List) % 2 != 0:
            middle_number = median(List)
            return st.median(List[:List.index(middle_number)])
        else:
            middle_index = len(List)//2
            middle_number = List[middle_index]
            return st.median(List[:List.index(middle_number)])
    else:
        return None    

#Question 9
#Write a python function implementing a function that returns the first quantile of a set of numbers
def third_quartile(List):
    if len(List) >= 4:
        List.sort()
        if len(List) % 2 != 0:
            middle_number = median(List)
            return st.median(List[List.index(middle_number):])
        else:
            middle_index = len(List)//2
            middle_number = List[middle_index]
            return st.median(List[List.index(middle_number):])
    else:
        return None    

def quartile_analysis(data):
    q1 = first_quartile(data)
    q3 = third_quartile(data)
    median = st.median(data)
    if abs(median - q1) > abs(median - q3):
        return abs(median - q1)
    else:
        return abs(median - q3)

def big_picture_analysis(labor_data):
    categories = set([elem.labor_category for elem in labor_data])
    central_tendency = []
    spread = []
    outliers = []
    iqrs = []
    for category in categories:
        data = LaborCategory.objects.filter(labor_category=category).all()
        prices = [round(float(elem.price),2) for elem in data]
        if len(prices) > 5 and stats.normaltest(prices).pvalue > 0.05:
            spread.append([category, st.stdev(prices)])
            central_tendency.append([category, st.mean(prices)])
        else:
            spread.append([category, quartile_analysis(prices)])
            central_tendency.append([category, st.median(prices)])
        outliers.append([category, count_outliers(prices)])
    bar_plot(central_tendency,"center.html")
    bar_plot(spread,"spread.html")
    bar_plot(outliers,"outlier_count.html")
    print("central tendency",st.median([elem[1] for elem in  central_tendency]))
    print("spread",st.median([elem[1] for elem in spread]))
    print("outliers",st.median([elem[1] for elem in outliers]))


def plot_individual_timeseries(data,years,category):
    x_vals = []
    y_vals = []
    for year in years:
        try:
            y_vals.append(data[year])
            x_vals.append(year)
        except:
            continue
    plotly.offline.plot({
        "data":[Scatter(x=x_vals,y=y_vals)],
        "layout":Layout(
            title=category
        )
    },auto_open=False)
    category = category.replace("/","_").replace(",","_")
    
    category = "_".join(category.lower().split())
    if len(category) > 40:
        category = category.split("_")[0]
    shutil.move("temp-plot.html","/Users/ericschles/Documents/projects/calc/price_prediction/viz/"+category+".html")     

        
class Command(BaseCommand):
    #do year over year analysis
    def handle(self, *args, **options):
        spread_data = OverallSpread.objects.all()
        categories = set([elem.labor_category for elem in spread_data])
        years = list(set([int(elem.year) for elem in spread_data]))
        years.sort()
        overall_spread = {}.fromkeys(categories, {}.fromkeys(years,0))
        for category in categories:
            objects = OverallSpread.objects.filter(labor_category=category).all()
            for object in objects:
                if not is_nan(float(object.spread)):
                    overall_spread[object.labor_category][int(object.year)] = float(object.spread)


        spread_change_first_to_last = []
        positive_negative_first_to_last = []
        most_recent_change = []
        most_recent_change_pos_neg = []
        change_period_over_period = []
        change_year_over_year = []
        lengths = []
        for category in categories:
            tmp = []
            data = []
            #years are in sorted order
            for year in years:
                if overall_spread[category][year] != 0:
                    data.append(overall_spread[category][year])
                else:
                    continue
            lengths.append(len(data))
        maximum_length = max(lengths)
        for _ in range(maximum_length):
            change_period_over_period.append([])
        for category in categories:
            tmp = []
            data = []
            #years are in sorted order
            for year in years:
                if overall_spread[category][year] != 0:
                    data.append(overall_spread[category][year])
                else:
                    continue
            spread_change_first_to_last.append(data[-1] - data[0])
            if data[-1] - data[0] > 0:
                positive_negative_first_to_last.append(1)
            elif data[1] - data[0] == 0:
                positive_negative_first_to_last.append(0)
            else:
                positive_negative_first_to_last.append(-1)
            if len(data) > 2:
                most_recent_change.append(data[-1] - data[-2])
                if data[-1] - data[-2] > 0:
                    most_recent_change_pos_neg.append(1)
                elif data[1] - data[-2] == 0:
                    most_recent_change_pos_neg.append(0)
                else:
                    most_recent_change_pos_neg.append(-1)
                #sharding our data
                for index,val in enumerate(data[1:]):
                    tmp.append(data[index] - data[index-1])
                for length in range(maximum_length):
                    try:
                        change_period_over_period[length].append(tmp[length])
                    except:
                        break
        ave_change_period_over_period_for_each_period = []
        for elem in change_period_over_period:
            if len(elem) > 2:
                ave_change_period_over_period_for_each_period.append(st.mean(elem))
        print("analysis of change in spread from beginning to end:")
        print("average change in spread from beginning of record to end",st.mean(spread_change_first_to_last))
        print("standard deviation of change in spread from beginning of record to end",st.stdev(spread_change_first_to_last))
        print("average change in direction of spread from beginning of record to end",st.mean(positive_negative_first_to_last))
        print("standard deviation of change in direction of spread from beginning of record to end",st.stdev(positive_negative_first_to_last))

        print("analysis of most recent change in spread:")
        print("most recent average change in spread over average",st.mean(most_recent_change))
        print("standard deviation of change in spread most recently",st.stdev(most_recent_change))
        print("average change in direction of spread most recently",st.mean(most_recent_change_pos_neg))
        print("standard deviation of change in direction of spread most recently",st.stdev(most_recent_change_pos_neg))
        
        print("average change period over period")
        for index, val in enumerate(ave_change_period_over_period_for_each_period):
            print(index, val)
