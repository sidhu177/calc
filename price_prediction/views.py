from django.shortcuts import render
from price_prediction.models import FittedValuesByCategory
from price_prediction.models import LaborCategoryLookUp
from price_prediction.models import PriceModels
from contracts.models import Contract

def prepare_data_for_plotting(data,fitted_values):
    #When x = Contract.objects.all()[0]; is x.contract_start the same as Being Date in the spreadsheet?
    dicter = {}
    dicter["x_data"] = [datum.contract_start for datum in data]
    dicter["y_data"] = [datum.hourly_rate_year1 for datum in data]
    dicter["x_fitted"] = [fitted_value.start_date for fitted_value in fitted_values]
    dicter["y_fitted"] = [fitted_value.fittedvalue for fitted_value in fitted_values]
    return dicter

# Create your views here.
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
        return render(request, "calc_kpi/timeseries_visual.html",context)
    elif request.method == "GET":
        return render(request, "calc_kpi/timeseries_visual.html",{"result":False})

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
