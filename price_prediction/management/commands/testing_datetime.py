from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

def find_current_option_startdate(export_date, begin_date, option_years=5):
    # Jan 4th 2017
    # =1/4/2017-(1/9/2004+5+5)
    years_of_contract = (export_date - begin_date).days/365.2425
    num_option_periods = years_of_contract // option_years
    return begin_date + relativedelta( years=int(num_option_periods*option_years) )

def calculate_current_contract_year(export_date, begin_date, option_years=5):
    years_of_contract = (export_date - begin_date).days/365.2425
    num_option_periods = years_of_contract // option_years
    tmp = round((export_date - (begin_date + relativedelta(years=int(option_years * num_option_periods)))).days/365.2425)
    return round((export_date - (begin_date + relativedelta(years=int(option_years * num_option_periods)))).days/365.2425)

if __name__ == '__main__':
    df = pd.read_excel("MostCurrentLaborCategories_01_04_2017.xlsx")
    for index in df.index:
        
        if (df.ix[index]["Contract Year"] - calculate_current_contract_year(datetime(2017,1,4), df.ix[index]["Begin Date"])) > 1:
            import code
            code.interact(local=locals())
        
            
        
