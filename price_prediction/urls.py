
from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^timeseries_analysis',views.timeseries_analysis,name="timeseries_analysis")
    #I don't remember if this is right...following https://docs.djangoproject.com/en/1.10/intro/tutorial01/
]
