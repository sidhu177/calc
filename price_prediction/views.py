from django.shortcuts import render
from price_prediction.models import FittedValuesByCategory
from price_prediction.models import LaborCategoryLookUp
from price_prediction.models import PriceModels
from contracts.models import Contract
import json

def prepare_data_for_plotting(data,fitted_values):
    #When x = Contract.objects.all()[0]; is x.contract_start the same as Being Date in the spreadsheet?
    dicter = {}
    timestamps = [str(datum.contract_start) for datum in data]
    timestamps = [timestamp.split(" ")[0] for timestamp in timestamps]
    dicter["x_data"] = ["x"] + timestamps
    dicter["x_data"] = json.dumps(dicter["x_data"])
    dicter["y_data"] = ["observed prices"] + [float(datum.hourly_rate_year1) for datum in data]
    dicter["y_data"] = json.dumps(dicter["y_data"])
    dicter["y_fitted"] = ["fitted prices"] + [float(fitted_value.fittedvalue) for fitted_value in fitted_values]
    dicter["y_fitted"] = json.dumps(dicter["y_fitted"])
    return dicter


def timeseries_analysis(request):
    """
    This method takes in a labor category and returns a timeseries visualization of the labor category.
    This includes the original time series, predicted pricing for the next 5 years and textual analysis of the data being presented
    """
    if request.method == 'POST':
        post_data_dict = request.POST.dict()
        labor_category = post_data_dict["labor_category"]
        results = Contract.objects.filter(labor_category=labor_category)
        fitted_values = FittedValuesByCategory.objects.filter(labor_key=labor_category)
        context = prepare_data_for_plotting(results,fitted_values)
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
