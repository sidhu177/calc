from django.db import models

class LaborCategory(models.Model):
    labor_category = models.CharField(max_length=400)
    date = models.DateField()
    price = models.DecimalField(decimal_places=2, max_digits=200)

    def __str__(self):
        return str(self.labor_category) +":"+ str(self.price)
    
class DecompressLaborCategory(models.Model):
    labor_category = models.CharField(max_length=400)
    labor_key = models.CharField(max_length=400)

    def __str__(self):
        return self.labor_key +":"+ self.labor_category

class LaborCategoryLookUp(models.Model):
    labor_category = models.CharField(max_length=400)
    labor_key = models.CharField(max_length=400)
    labor_value = models.CharField(max_length=400)
    start_date = models.DateField()

    def __str__(self):
        return self.labor_key + ":" + self.labor_value

class PriceModels(models.Model):

    # it actually makes sense to make this a foreign key,
    # given the way it's used
    # in price_prediction/management/commands/generate_arima_model.py
    labor_category = models.CharField(max_length=400)
    labor_key = models.CharField(max_length=400)
    model = models.BinaryField()

class FittedValuesByCategory(models.Model):
    labor_category = models.CharField(max_length=400)
    labor_key = models.CharField(max_length=400)
    upper_bound = models.DecimalField(decimal_places=2, max_digits=200)
    fittedvalues = models.DecimalField(decimal_places=2, max_digits=200)
    lower_bound = models.DecimalField(decimal_places=2, max_digits=200)
    start_date = models.DateField()

    def __str__(self):
        return self.labor_key

class OneYearFitted(models.Model):
    labor_category = models.CharField(max_length=400)
    labor_key = models.CharField(max_length=400)
    upper_bound = models.DecimalField(decimal_places=2, max_digits=200)
    fittedvalues = models.DecimalField(decimal_places=2, max_digits=200)
    lower_bound = models.DecimalField(decimal_places=2, max_digits=200)
    start_date = models.DateField()

    def __str__(self):
        return self.labor_key

class TwoYearsFitted(models.Model):
    labor_category = models.CharField(max_length=400)
    labor_key = models.CharField(max_length=400)
    upper_bound = models.DecimalField(decimal_places=2, max_digits=200)
    fittedvalues = models.DecimalField(decimal_places=2, max_digits=200)
    lower_bound = models.DecimalField(decimal_places=2, max_digits=200)
    start_date = models.DateField()

    def __str__(self):
        return self.labor_key

class TrendByCategory(models.Model):
    labor_category = models.CharField(max_length=400)
    labor_key = models.CharField(max_length=400)
    trend = models.DecimalField(decimal_places=2, max_digits=200)
    start_date = models.DateField()

    def __str__(self):
        return self.labor_key
