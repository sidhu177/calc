from price_prediction.models import FittedValuesByCategory
from price_prediction.models import LaborCategoryLookUp
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

# this comes from here:
# http://stackoverflow.com/questions/22770352/auto-arima-equivalent-for-python

def objective_function(data, order):
    return sm.tsa.ARIMA(data, order).fit().aic


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
            return order, obj_func(order)

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
        return order, obj_func(order)

    except:  # however we don't always meet invertibility conditions
        # Here we explicitly test for a single MA
        # or AR process being a better fit
        # If either has a lower (better) aic score we return that model order
        model_ar_one = sm.tsa.ARIMA(data, (1, 0, 0)).fit()
        model_ma_one = sm.tsa.ARIMA(data, (0, 0, 1)).fit()
        if model_ar_one.aic < model_ma_one.aic:
            return (1, 0, 0), obj_func((1, 0, 0))
        else:
            return (0, 0, 1), obj_func((0, 0, 1))


def model_search(data):
    """
    Optimizers supported:
    * brute
    """
    print("got to start of model search")
    results = []
    results.append(brute_search(data))
    min_score = 100000000
    best_order = ()
    for result in results:
        if result[1] < min_score:
            min_score = result[1]
            best_order = result[0]
    return best_order

def date_to_datetime(time_string):
    
    return datetime.datetime.strptime(time_string, '%m/%d/%Y')

def ave_error(values, fitted_values):
    
    if (len(values) == len(fitted_values)) or (len(values) < len(fitted_values)):
        ave_errors = [abs(values[ind] - fitted_values[ind]) for ind in range(len(values))]
        return sum(ave_errors)/len(values) 
    else:
        ave_errors = [abs(values[ind] - fitted_values[ind]) for ind in range(len(fitted_values))] 
        return sum(ave_errors)/len(values)
    
def check_for_extreme_values(sequence, sequence_to_check=None):
    mean = statistics.mean(sequence)
    stdev = statistics.stdev(sequence)
    if sequence_to_check != None:
        for val in sequence_to_check:
            if val >= mean + (stdev*2):
                sequence_to_check.remove(val)
            elif val <= mean - (stdev*2):
                sequence_to_check.remove(val)
        return sequence_to_check
    else:
        for val in sequence:
            if val >= mean + (stdev*2):
                sequence.remove(val)
            elif val <= mean - (stdev*2):
                sequence.remove(val)
        return sequence
        
def setting_y_axis_intercept(data, model):
    try:
        # if we are using the original data
        data = list(data["Price"])
    except:
        # if we are using the deseasonalized data
        data = list(data)
    fittedvalues = list(model.fittedvalues)
    avg = statistics.mean(data)
    median = statistics.median(data)
    possible_fitted_values = []

    possible_fitted_values.append([elem + avg for elem in fittedvalues])
    possible_fitted_values.append([elem + data[0] for elem in fittedvalues])
    possible_fitted_values.append([elem + median for elem in fittedvalues])
    possible_fitted_values.append(fittedvalues)
    min_error = 1000000
    best_fitted_values = 0
    for ind, f_values in enumerate(possible_fitted_values):
        avg_error = ave_error(data, f_values)
        if avg_error < min_error:
            min_error = avg_error 
            best_fitted_values = ind
    print("minimum error:", min_error)
    return possible_fitted_values[best_fitted_values]

def check_for_extreme_values(sequence, sequence_to_check=None):
    mean = statistics.mean(sequence)
    stdev = statistics.stdev(sequence)
    if sequence_to_check != None:
        for val in sequence_to_check:
            if val >= mean + (stdev*2):
                sequence_to_check.remove(val)
            elif val <= mean - (stdev*2):
                sequence_to_check.remove(val)
        return sequence_to_check
    else:
        for val in sequence:
            if val >= mean + (stdev*2):
                sequence.remove(val)
            elif val <= mean - (stdev*2):
                sequence.remove(val)
        return sequence
        
def trend_predict(data):
    # seasonal decompose 
    if len(data) > 52:
        s = sm.tsa.seasonal_decompose(data["Price"], freq=52)
    elif len(data) > 12:
        s = sm.tsa.seasonal_decompose(data["Price"], freq=12)
    else:
        return None
    # clearing out NaNs
    new_data = s.trend.fillna(0)
    new_data = new_data.iloc[new_data.nonzero()[0]]
    model_order = list(model_search(new_data))
    model_order = tuple([int(elem) for elem in model_order])
    model = sm.tsa.ARIMA(new_data, model_order).fit()
    model.fittedvalues = setting_y_axis_intercept(new_data, model)
    return model, new_data, model_order

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
        string = string.replace("$", "").replace(",", "")
        return float(string)
    else:
        return string

