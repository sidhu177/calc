from django.shortcuts import render
from price_prediction.models import FittedValuesByCategory
from price_prediction.models import LaborCategoryLookUp
from price_prediction.models import PriceModels
from price_prediction.models import DecompressLaborCategory
from price_prediction.models import TrendByCategory
from contracts.models import Contract
import json

def prepare_data_for_plotting(data, fitted_values, trended_values):
    #When x = Contract.objects.all()[0]; is x.contract_start the same as Being Date in the spreadsheet?
    data_object = []
    date_lookup = {}
    for ind,datum in enumerate(data):
        tmp = {}
        timestamp = str(datum.contract_start)
        timestamp = timestamp.split(" ")[0]
        tmp["date"] = timestamp
        date_lookup[timestamp] = ind
        tmp["observed"] = float(datum.hourly_rate_year1)
        data_object.append(tmp)
    for ind,value in enumerate(fitted_values):
        tmp = {}
        timestamp = str(value.start_date)
        timestamp = timestamp.split(" ")[0]
        if timestamp in date_lookup.keys():
            data_object[date_lookup[timestamp]]["fitted"] = float(value.fittedvalue)
            data_object[date_lookup[timestamp]]["lower_bound"] = float(value.lower_bound)
            data_object[date_lookup[timestamp]]["upper_bound"] = float(value.upper_bound)
        else:
            tmp["date"] = timestamp
            tmp["fitted"] = float(value.fittedvalue)
            tmp["lower_bound"] = float(value.lower_bound)
            tmp["upper_bound"] = float(value.upper_bound)
            data_object.append(tmp)
    for ind,value in enumerate(trended_values):
        tmp = {}
        timestamp = str(value.start_date)
        timestamp = timestamp.split(" ")[0]
        if timestamp in date_lookup.keys():
            data_object[date_lookup[timestamp]]["trend"] = float(value.trend)
        else:
            tmp["date"] = timestamp
            tmp["trend"] = float(value.trend)
            data_object.append(tmp)
            
    return {"data_object": json.dumps(data_object)}


def timeseries_analysis(request):
    """
    This method takes in a labor category and returns a timeseries visualization of the labor category.
    This includes the original time series, predicted pricing for the next 5 years and textual analysis of the data being presented
    """
    if request.method == 'POST':
        post_data_dict = request.POST.dict()
        labor_category = post_data_dict["labor_category"]
        results = Contract.objects.filter(labor_category=labor_category)
        compress = DecompressLaborCategory.objects.filter(labor_category=labor_category)
        fitted_values = FittedValuesByCategory.objects.filter(labor_key=compress[0].labor_key)
        trended_values = TrendByCategory.objects.filter(labor_key=compress[0].labor_key)
        context = prepare_data_for_plotting(results, fitted_values, trended_values)
        return render(request, "price_prediction/timeseries_visual.html",context)
    elif request.method == "GET":
        return render(request, "price_prediction/timeseries_visual.html",{"result":False})

#Work flow:

#User chooses labor category
#A graph is populated for the labor category with:
# * hourly rates over time for the given labor category (check)
# * prediction range of what the prices could be over the next 5 years (check) ~
# pass data to the front end (check)
# set up urls
# * showing trend analysis - ToDo
# * showing upper bound price ToDo
# * showing lower bound price ToDo

#Things we need to take in:
# labor category
#
#Things we need to return:
# Contract by labor category over time
# 
