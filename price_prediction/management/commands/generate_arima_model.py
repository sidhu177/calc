from price_prediction.models import FittedValuesByCategory as Fitted
from price_prediction.models import LaborCategory
from price_prediction.models import TrendByCategory as Trend
import pandas as pd
import math
import datetime
import statsmodels.api as sm
import statistics
from functools import partial
import code
from scipy.optimize import brute
from django.core.management import BaseCommand
from optparse import make_option
import matplotlib.pyplot as plt
import numpy as np
import asyncio

MINIMUM_WAGE=10.20

# this comes from here:
# http://stackoverflow.com/questions/22770352/auto-arima-equivalent-for-python

def objective_function(data, order):
    return sm.tsa.ARIMA(data, order).fit(disp=0).aic


def brute_search(data):
    print("got here with no errors")
    obj_func = partial(objective_function, data)
    # Back in graduate school professor Lecun said in class that ARIMA models
    # typically only need a max parameter of 5, so I doubled it just in case.
    upper_bound_AR = 10
    upper_bound_I = 10
    upper_bound_MA = 10
    grid_not_found = True
    while grid_not_found:
        try:
            if upper_bound_AR < 0 or upper_bound_I < 0 or upper_bound_MA < 0:
                grid_not_found = False
            grid = (
                slice(1, upper_bound_AR, 1),
                slice(1, upper_bound_I, 1),
                slice(1, upper_bound_MA, 1)
            )
            order = brute(obj_func, grid, finish=None)
            return order

        except Exception as e:
            error_string = str(e)
            if "MA" in error_string:
                upper_bound_MA -= 1
            elif "AR" in error_string:
                upper_bound_AR -= 1
            else:
                upper_bound_I -= 1

    # assuming we don't ever hit a reasonable set of upper_bounds,
    # it's pretty safe to assume this will work
    try:
        grid = (
            slice(1, 2, 1),
            slice(1, 2, 1),
            slice(1, 2, 1)
        )
        order = brute(obj_func, grid, finish=None)
        return order

    except:  # however we don't always meet invertibility conditions
        # Here we explicitly test for a single MA
        # or AR process being a better fit
        # If either has a lower (better) aic score we return that model order
        try:
            model_ar_one = sm.tsa.ARIMA(data, (1, 0, 0)).fit(disp=0)
            model_ma_one = sm.tsa.ARIMA(data, (0, 0, 1)).fit(disp=0)
        except:
            return None
        if model_ar_one.aic < model_ma_one.aic:
            return (1, 0, 0)
        else:
            return (0, 0, 1)


def date_to_datetime(time_string):
    return datetime.datetime.strptime(time_string, '%m/%d/%Y')

    
# create a monthly continuous time series to pull from
# interpolate values from trend
# set prediction from new values from artificially generated time series.


def check_for_extreme_values(sequence, sequence_to_check=None):
    print("started check")
    data = [sequence.ix[i].Price for i in sequence.index]
    print("moved things to a list")
    final_data = []
    for elem in data:
        try:
            len(elem)
            for i in range(len(elem)):
                final_data.append(float(elem[i]))
        except:
            final_data.append(elem)
    print("finished for loop")
    print("finished post processing")
    sequence = final_data[:]
    mean = statistics.mean(sequence)
    stdev = statistics.stdev(sequence)
    if sequence_to_check is not None:
        for val in sequence_to_check:
            if val >= mean + (stdev*2):
                sequence_to_check.remove(val)
            elif val <= mean - (stdev*2):
                sequence_to_check.remove(val)
        return sequence_to_check
    else:
        for val in sequence:
            if val >= mean + (stdev*2):
                return True
            elif val <= mean - (stdev*2):
                return True
        return False

def remove_extreme_values(sequence, sequence_to_check=None):    
    data = [float(sequence.ix[i]) for i in sequence.index]
    print("moved things to a list")
    
    mean = statistics.mean(data)
    stdev = statistics.stdev(data)
    print("created mean, std")
    new_sequence = sequence.copy()
    for ind,val in enumerate(data):
        if val >= mean + (stdev*2):
            new_sequence = new_sequence.drop(sequence.index[ind])
        elif val <= mean - (stdev*2):
            new_sequence = new_sequence.drop(sequence.index[ind])
    print("removed bad values")
    return new_sequence

    
def clean_data(data):
    new_data = pd.DataFrame()
    for timestamp in set(data.index):
        if len(data.ix[timestamp]) > 1:
            tmp_df = data.ix[timestamp].copy()
            new_price = statistics.median([tmp_df.iloc[index]["Price"] for index in range(len(tmp_df))])
            series = tmp_df.iloc[0]
            series["Price"] = new_price
            new_data = new_data.append(series)
        else:
            new_data = new_data.append(data.ix[timestamp])
    return new_data


def date_range_generate(start,end):
    start_year = int(start.year)
    start_month = int(start.month)
    end_year = int(end.year)
    end_month = int(end.month)
    dates = [datetime.datetime(year=start_year, month=month, day=1) for month in range(start_month, 13)]
    for year in range(start_year+1, end_year+1):
        dates += [datetime.datetime(year=year, month=month, day=1) for month in range(1,13)]
    return dates


def interpolate(series):
    date_list = list(series.index)
    date_list.sort()
    dates = date_range_generate(date_list[0], date_list[-1])
    for date in dates:
        if date not in list(series.index):
            series = series.set_value(date, np.nan)
    series = series.interpolate(method="values")
    to_remove = [elem for elem in list(series.index) if elem.day != 1]
    series.drop(to_remove, inplace=True)
    return series


def check_for_singular(data):
    if len(set([data.ix[index]["Price"] for index in data.index])) == 1:
        return True
    else:
        return False

#break out seasonal decomposition code
#test to make sure model_order is consistently returning same result for same data
#test flow of control like before
#test to make sure the same extreme values are consistently removed for the same data
#make sure clean data returns consistent result
#check_for_singular code to make sure it works as expected
#check generate_date_range
#check the return statements - mypy

def trend_predict(data):
    print("inside of trend predict")
    cleaned_data = clean_data(data)
    print("finished cleaning data")
    if check_for_singular(cleaned_data):
        return None
    print("checked for singularity")
    # seasonal decompose
    data = data.dropna()
    if len(data) > 52:
        trend = sm.tsa.seasonal_decompose(data["Price"], freq=52).trend
    elif len(data) > 12:
        trend = sm.tsa.seasonal_decompose(data["Price"], freq=12).trend
    else:
        return None
    print("finished creating trend")
    trend = trend.fillna(0)
    trend = trend.iloc[trend.nonzero()[0]]
    s = cleaned_data.T.squeeze()
    s.sort_index(inplace=True)
    print("sorted index by date")
    # clearing out NaNs
    new_data = s.fillna(0)
    new_data = new_data.iloc[new_data.nonzero()[0]]
    interpolated_data = interpolate(new_data.copy())
    print("interpolated data")
    interpolated_data = remove_extreme_values(interpolated_data)
    print("removed extreme data")
    model_order = brute_search(interpolated_data)
    if model_order is  None:
        return None
    else:
        model_order = list(model_order)
    print("model order decided")
    model_order = tuple([int(elem) for elem in model_order])
    #model_order = (1,0,0)
    try:
        model = sm.tsa.ARIMA(interpolated_data, model_order).fit(disp=0)
    except:
        import code
        code.interact(local=locals())
    print("fit model")
    forecast = model.forecast(steps=60)
    print("forecasted future")
    tmp_date = interpolated_data.index[-1]
    end_date = datetime.datetime(year=tmp_date.year+5, month=tmp_date.month, day= tmp_date.day)
    date_range = date_range_generate(interpolated_data.index[-1], end_date)
    print("leaving trend predict")
    return date_range, forecast, trend

def is_nan(obj):
    if type(obj) == type(float()):
        return math.isnan(obj)
    else:
        return False

#make sure it's possible to connect to the database
#make sure each branch of my code is exercises.
#write a test for each every if, else statement
#stringio instance via monkey patching
#test to make sure minimum_wage is used throughout!!!

async def main(labor_category):
    labor_objects = LaborCategory.objects.filter(labor_category=labor_category)
    if len(labor_objects) < 12: #there isn't enough data for a prediction in this case
        return
    print("completed lookup")
    df = pd.DataFrame()
    for labor_object in labor_objects:
        df = df.append({
            "Date": labor_object.date,
            "Price": float(labor_object.price)
        }, ignore_index=True)
    # sanity checking this is a datetime
    print("created dataframe")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    df.sort_index(inplace=True)
    print("completed dataframe sorting")
    result = trend_predict(df)
    print("finished prediction")
    if result:
        date_range, forecast, trend = result
    else:
        return
    print("got result")
    for i in range(len(forecast[0])):
        if float(forecast[2][i][0]) < MINIMUM_WAGE:
            fitted = Fitted(labor_key=labor_category,
                        lower_bound=MINIMUM_WAGE,
                        fittedvalues=forecast[0][i],
                        upper_bound=forecast[2][i][1],
                        start_date=date_range[i])
        else:
            fitted = Fitted(labor_key=labor_category,
                            lower_bound=forecast[2][i][0],
                            fittedvalues=forecast[0][i],
                            upper_bound=forecast[2][i][1],
                            start_date=date_range[i])
        fitted.save()
        print("saved fitted values")
        print("finished Fitted values")
        for ind in range(len(trend)):
            trend_elem = Trend(labor_key=labor_category,
                               trend=trend[ind],
                               start_date=trend.index[ind])
            trend_elem.save()
        print("Saved trend results")


class Command(BaseCommand):

    def handle(self, *args, **options):
        Fitted.objects.all().delete()
        Trend.objects.all().delete()
        labor_categories = [i for i in LaborCategory.objects.all() if i.labor_category]
        labor_categories = set([i.labor_category for i in labor_categories])
        loop = asyncio.get_event_loop()
        for index, labor_category in enumerate(labor_categories):
            loop.run_until_complete(main(labor_category))
        loop.close()
