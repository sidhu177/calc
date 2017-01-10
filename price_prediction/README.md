#Price Prediction

##Requirements

The following python packages are required to get things to work:

```
scipy==0.18.1
pandas==0.18.0
numpy==1.11.2
statsmodels==0.6.1
```

The following python packages are optional, but recommended, so that you can debug your models:

`matplotlib==1.5.1`

These optional dependencies can be found in requirements-dev.txt

##Justification of requirements

`statsmodels==0.6.1` - This is the heart of the application.  It has the time series model, which is used for price prediction.  

`scipy==0.18.1, pandas==0.18.0, numpy==1.11.2` - these three packages are dependencies for statsmodels.  

##How the requirements are used

In this section, we'll walk through specifically what parts of the packages that get used.  This way, if these dependencies become stale, either because compliance reasons or other issues, you'll know what you can update.  And what cannot be updated.

```python
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.optimize import brute
```

The above gives some insight into how the code is used.  Specifically, `scipy.optimize`'s `brute` method.  This method runs a brute force algorithm against a function passed in.  [Here are the docs for `brute`](https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.brute.html). 

Other than the brute method, which might be subject to change.  The rest of the code takes advantage of the basic utility of each of the above packages and is therefore unlikely to change.

##Explanation of codebase

This code is currently defined in the [data_analysis branch in the price_prediction subapp](https://github.com/18F/calc/tree/data_analysis/price_prediction). The additions to the code base represents a complete prototype - a data visualization, mathematical model with parameter tuning, and a set of data cleaning routines.  The data visualization comes from the [c3.js](http://c3js.org/) library, a high level, minimal data visualization library, built ontop of [d3.js](https://d3js.org/).  The mathematical model is called the AutoRegressive Integrated Moving Average model, or ARIMA for short.  Typically the ARIMA model is tuned manually via inspection of the partical autocorrelation function and autocorrelation functions associated with a given timeseries.  However by making use of the Akaike Information Criterion, shorted to AIC, and a simple hill climb algorithm, we are able to find hyper parameters to fit the curve.  Therefore no manual tunning is required.  The data cleaning techniques are typical and therefore will not be discussed in detail at this point.

The ARIMA model is the main value add of the prototype.  In fact, the ARIMA model is made of up two simpler models, the AutoRegressive model and the Moving Average model.  The the Moving Average is the easier of the two models to explain, so we'll begin with it.  

Implementing the MA model from scratch:

```python
import statistics as stat

def moving_average(data, sliding_window=2):
    averages = []
    terminal_condition = False
    start = 0
    end = sliding_window
    while end != len(data):
        averages.append(stat.mean(data[start:end]))
        start += 1
        end += 1
    return averages
```

As you can see above, we simply define a sliding window, and then take the average of the data incrementing over the index as we go.  Unfortunately the AutoRegressive piece is slightly harder to define.  For this, we'll need to bring in the statsmodels library and it's main work horse - linear regression.

```python
import statsmodels.api as sm

def autoregressive(data):
    Y = data[1:]
    X = data[:-1]
    model = sm.OLS(X,Y)
    result = model.fit()
    return [result.predict(x) for x in X]
```

The autoregressive model treats y_hat, the predicted value for the next data point, as it is correlated to the previous value.  Thus the AutoRegressive model assumes that each value is correlated, with the value in the previous time.

Both of the models we described above, are MA(1) and AR(1) processes - probabilistic mathematical equations, that occur over time.  The hyper parameters are more generally referred to as p and q, respectively.  The hyper parameter, p, refers to the size of the sliding window in the moving average process.  Where as the hyper parameter, q, refers to the number of terms to depend the next element in the series on, in the autoregressive process.  So if we are looking at an AR(2) process - we'd do the following:

```python
def autoregressive(data):
    Y = data[2:]
    X = [[elem, data[ind+1]] for ind,elem enumerate(data) if elem != data[-1]]

    model = sm.OLS(X,Y)
    result = model.fit()
    return [result.predict(x) for x in X]
```

Notice, now we predict the next result on the previous 2.  

The Integrated part of the ARIMA model, simply differences away individual observations, increasing the search space of the model, but allowing the model an increased sense of flexibility.

If you are interested in learning more about the ARIMA model or statistical modeling more generally, from scratch, check out this great resource:

[Statistics class at penn state](https://onlinecourses.science.psu.edu/stat501/node/358)

##Making use of the ARIMA model  

Now that we understand what the ARIMA model is, let's see how to put the interface into practice.

```python
from datetime import datetime
import pandas as pd
from functools import partial
from scipy import stats
import statsmodels.api as sm
from scipy.optimize import brute

def objective_function(data, order):
    return sm.tsa.ARIMA(data, order).fit().aic

def brute_search(data):
    obj_func = partial(objective_function, data)
    upper_bound_AR = 4
    upper_bound_I = 4
    upper_bound_MA = 4
    grid = (
        slice(1, upper_bound_AR, 1),
        slice(1, upper_bound_I, 1),
        slice(1, upper_bound_MA, 1)
    )
    order = brute(obj_func, grid, finish=None)
    return order, obj_func(order)


df = pd.DataFrame()

for _ in range(200):
    df = df.append({
        "Date": datetime(year=random.randint(2002, 2012), month=random.randint(1,13), day=1),
        "Value": random.randint(0,100000)
        }, ignore_index=True)
    print("created dataframe")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    df.sort_index(inplace=True)

model_order = brute_search(df)
model = sm.tsa.ARIMA(df, model_order).fit()
prediction = model.predict(0, len(df))
forecast = model.forecast(steps=10)
print(prediction)
print(forecast)
```

In order to tune the hyper parameters, p - AR, d - Integrated, and q - MA; we apply a hill climb algorithm.  This algorithm checks the resulting ARIMA model's [AIC](https://en.wikipedia.org/wiki/Akaike_information_criterion).  The set of hyper parameters that return the most minimal AIC are the hyper parameters chosen. 

Once the hyper parameters are chosen we simply run the model and then get our forecast.  The forecast method, predicts n equally spaced time steps into the future.  Where as the predict method fits the model to the same time intervals as the data.  Therefore exact spacing is not needed for predict, only for forecast.

Once we have our prediction, we are free to save the results to a database and then call them, as needed for our views.  

##Understanding the details

###Problems with the data sets

1. **The timestamps may not be completely meaningful.**  The timestamps associated with the data sets are the first year prices of the contract.  These negoiated hourly rates aren't the dates these contracts are negoiated, but instead, are the start dates of the contracts.  It's unclear if start date of the contract, is an acceptable time stamp for the contracts.  The data _seems_ to be fine, based on the fact that the start date, and the negoiated starting hourly rate are negoiated at the same time.  However, this may not actually make for a good starting time stamp.  In future datasets, we may want to consider adding a different timestamp for the start date - the date the contract was negoiated.  
2. **The timestamps are not evening distributed.**  This makes predicting into the future with the current interface, using the actual timestamps, impossible.  To compensate for this I've added an interpolation method that adds intermediate values, every month.  Then the original values are removed and the prediction takes place over the interpolated values.  Here's the code that does that:

```python
import datetime

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
```

Note that the series in this case is a pandas series.

3. **Some of the data is wrong**.  Some of the values in the dataset were input wrong and therefore make any predictions less useful.  To deal with this a short term fix has been developed:

```python
def check_for_extreme_values(sequence, sequence_to_check=None):
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
                sequence.remove(val)
            elif val <= mean - (stdev*2):
                sequence.remove(val)
        return sequence
```

4. **Some timestamps are repeated.**  Some of the timestamps are repeated in the timeseries.  This means the model tries to predict multiple outputs for a single input.  And it's unclear how the model handles this.  To deal with that, I wrote a method that cleans the dataset:

```python
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
```

##Operationalizing The Code

The above gives you a good sense of my motivation for the code base.  Unfortunately it is far from complete.  Without understanding the database tables or how the commands are run, this code is next to useless.  For one, each model takes a while to run.  If this code was run dynamically, with predictions updated on the fly, the application would be terribly slow.  For this reason, new data is read from a database, modeled, and then the newly modeled predictions are added back to the database.  

In order to generate a new prediction, from the top level directory run the following command:

`python manage.py generate_arima_model`

This allows us to make use of the arima model, as needed, when new data is added.  But also, it allows us the space to experiment with different prediction models.  By working with the framework, set up in this modeling code, but making use of a different timeseries model.  

Other models worthy of consideration:

* [Bayesian Simulation](https://en.wikipedia.org/wiki/Bayesian_probability)
    * [bayespy](https://github.com/bayespy/bayespy) - specifically [examples](https://github.com/bayespy/bayespy/tree/develop/bayespy/demos)
    * [PyMC](https://pymc-devs.github.io/pymc/tutorial.html)
* [BUGS (Bayesian Inference Using Gibbs Sampling)](https://en.wikipedia.org/wiki/Bayesian_inference_using_Gibbs_sampling)
    * [Some code from stackoverflow](http://stackoverflow.com/questions/27783670/how-to-implement-custom-gibbs-sampling-scheme-in-pymc)
* [Monte Carlo Simulation](https://en.wikipedia.org/wiki/Monte_Carlo_method)
    * [implement Monte Carlo Simulation on your own](https://pythonprogramming.net/monte-carlo-simulator-python/)
    * [A second tutorial](https://people.duke.edu/~ccc14/sta-663/MonteCarlo.html)
* [Recurrent Neural Networks](https://en.wikipedia.org/wiki/Recurrent_neural_network)
    * [Example with Keras](http://machinelearningmastery.com/time-series-prediction-lstm-recurrent-neural-networks-python-keras/)

##Preparing The Data To Be Modeled

Right now, the data comes to us first as CSVs.  The first thing we want to do is save that data to a database for further processing.  Trying to work directly on the pandas dataframes, is very slow.  It's much faster to store the data in a database and read it into memory on an as needed basis as a dataframe.  

The data is organized by labor category - however there isn't enough data in most labor categories to form a suitable timeseries prediction.  Therefore higher level buckets based on semantic information was used, to create a robust set of predictions.  

The data was bucketed across three strata:

* Education Level
* Years of Experience
* Schedule

It is worth noting at this point, that eventually the schedule will be phased out and replaced by SIN numbers, denoting a more fine grained schedule.  At this point, the code will need to be updated, to account for a clustering scheme.  Perhaps instead of via some semantic metric, by first partitioning data by years of experience and then education level.  From there the third partition could be via some clustering scheme.  I'd recommend [DBSCAN](http://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html).  

After the data was bucketed, it was saved to the database, with the original labor category, it's higher level categorization, it's contract start year, and the hourly starting price for the contractor.  

All of that takes place via the `load_lookup_data` command.  It is called like so:

`python manage.py load_lookup_data -f [path to file]`

##Models && Views

The models and views appear in the price_prediction module and correspond to the modeling routines defined above.

##The Data Visualization

As stated above, the data visualization is done via c3.js.  As you can see the code is fairly minimal, mostly relying on json formatting.

```javascript
chart = c3.generate({
    data: {
        x: 'date',
        xFormat: '%Y-%m-%d',
        json: {{data_object|safe}},
        keys: {
            x: 'date',
            value: [ "observed", "fitted", "trend" ]
        }
    },
    axis: {
        x: {
            type: "timeseries",
            tick: {
                format: '%Y-%m-%d'
            }
        }
    },
    line: {
        connectNull: true
    }
});
```

There are two things to note here that are atypical -

`keys` in the `data` object - This has three values: `observed`, `fitted`, `trend` - `observed` refers to the observed data found in the dataset.  Whereas, `fitted` refers to the data generated via our modeling routine.  And the `trend` refers to the general trend of the data.  If the `trend` is increasing over time, we can say prices are likely to rise, over the long term, rather than be variable via some seasonal or short term market forces.  If the `trend` is decreasing over time, we should expect long term prices to fall.  The trend line may be the most important, as it gives an eyeball view of whether we should expect prices to increase or decrease over the long term.  Which will inform how aggressively contracting officers should negotiate for future contracts.  And where savings can be expected.

The second thing to note is the `line` subobject - this connects the lines.  Because there isn't one time scale used in the dataset, we must add datapoints, piecemeal, one at a time, as seperate objects.  

The `data_object` which is passed in from the backend, is in fact a list of smaller javascript objects.  

The parameter `connectNull: true`, gives the objects the appearance of being connected, although from c3.js's perspective they are disjoint objects.  The reason the c3 library knows which objects to connect, is by the keys passed in.  This is denoted in the `value: ["observed", "fitted", "trend"]`.  The key associated with the data indicates which line a given element should be joined to.

##Intepretting the model's results

###Interpretation for Contracting Officers

![trend prediction](https://github.com/18F/calc/blob/data_analysis/price_prediction/trend_prediction.png)

As you can see from the above picture there are a number of useful pieces to this graph.

Let's start with the observed data:

The observed data shows us that Analyst 1's contracts were created sparsely at first and starting at around february 4th 2015, started increasing in volume.  This data also shows that the price started to vary wildly over that small term.  This gives us a sense about not all the data, but about the organization - as we moved to better understand semantically what the term Analyst 1 even means, there were wide variances in price.  Perhaps some people interpretted Analyst 1 to mean the strongest or best Analyst.  Whereas others took it to mean the lowest grade, or most junior analyst.  However, such analysis is merely conjecture.  Another possible conjecture, is that the agency, type of work, and location factors account for the wild swing in price.  Since we don't have data concerning these other qualities, we can't include them in the analysis or say anything for certain at this point.  However, by looking at this time series view can say far more about the price then we could before.

Note:  The observed data refers to the labor category.  The prediction refers to the higher level categorization.  

Let's look at the trend data:

The trend data gives us another view of how prices are changing over time.  It's interesting to see that prices for Analyst 1's have been falling over time, with a fair amount of distinction.  At least, until the wide variance in prices started up in 2015.  

Let's look at the prediction:

As you can see this point prediction, shows a forecasted value.  This forecast doesn't capture specific features of about the time series, however gives a prediction of where the trend of the data is likely headed.  Based on the passed data, I'd say this is a fairly accurate prediction of the trend.  Assuming that price variability remains high, the trend of the variability is likely to be towards the center of the variability, which the prediction dictates.

###Interpretation for Managers

As of right now there isn't a set of visualizations for managers, however one could easily be created using the existing framework.  

The idea would be a views of the data over time.  The visualization would give the manager the ability to view all the time series on a single graph, filter down to comparing two time series visualizations side by side, and filtering time series visualization by contracting officer who worked on contracts.  

Analysis this would provide:

1. a sense of how price negotiations are going in aggregate, over time
2. a sense of how well a given contracting officer negotiates prices, for a specific contract type
3. a sense of how well a given contracting officer negoiates prices, across multiple contract types

The second and third type of analysis would include trend lines, showing whether or not the price grew or fell over time for that contract type and if the contracting officer was able to continue to push down price over time.

###Definite Future Features

1. **Dealing with Lack Of Data**.  As of right now, I don't have anything visual when there is a lack of data.  I feel like this should probably decided by design / a word smith.  So I didn't design it on purpose, but it should be in the final product.

2. **95% confidence interval for prediction**.  At present a point statistic for the prediction is shown.  We should A/B test whether or not showing the lower and upper bound for the prediction is useful or confusing.  This already exists more or less in the code base.  


###Possible Future Features

_Geographic Time Series Analysis:_

If geographic information about where the contract is included, a more thorough analysis can be completed, including cost of living adjustment, analysis of how prices vary geographically over time, further segmentation of labor categories based on location.

Specifics about the geographic information, of interest:

* Location(s) where the contractor is living
* Location(s) of any other contractors who will be working with this contractor

_Inclusion of Bureau of Labor Statistics Data:_

It appears as though this [org - data at work](http://dataatwork.org/) has put together an api for BLS data. They have  a [general purpose fetcher](https://github.com/frictionlessdata/datapackage-py) that we could use to grab BLS employment data from [here - a datapackage website](http://data.okfn.org/data) that data at work, put together.  

If we could include BLS data then we could show the rate at which contracting officers prices specific labor needs, against what the market rates for that labor is.  Using this, we could define a metric which measures the difference between the rate a contracting officer negotiated for and the current labor rate for the labor category.  We could use this metric to tune training for current employees about specific markets.  So for instance, say contracting officers do not accurately price database administrators, compared to BLS data.  Then we could train the contracting officers in the fields they don't know well.  Either by bringing in recruiters, having the more skilled COs work with the less skilled COs, who understand those labor categories better, or some third mechanism.

_Only Installing Data Science Packages Locally_:

Technically, all that needs to live on the server is the prediction data.  We could do all the modeling stuff locally and then push the results up to the server for visualization.  This however would mean, the modeling command would need to be run every time new data is added.  Long term we could also have a seperate environment for running the modeling that passes the data back to the calc server space and saves data via some sort of web hook.  This would allow us the ability to run the modeling piece from a cluster environment.  People seem to be asking for cloud.gov to support cluster computing.  Over the long term, I could see this happening.  And calc could be the first to make use of a cluster environment effectively.





