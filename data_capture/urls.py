from django.conf.urls import include, url

from .views import (price_list_upload, bulk_upload, price_lists,
                    price_list_replace)

urlpatterns = [
    url(r'^step/', include(price_list_upload.steps.urls)),
    url(r'^step/3/errors$', price_list_upload.step_3_errors,
        name='step_3_errors'),
    url(r'^bulk/region-10/step/', include(bulk_upload.steps.urls)),
    url(r'^price-lists$', price_lists.list_price_lists,
        name="price_lists"),
    url(r'^price-lists/(?P<id>[0-9]+)$', price_lists.price_list_details,
        name="price_list_details"),

    url(r'^price-lists/(?P<id>[0-9]+)/replace/step/',
        include(price_list_replace.steps.urls)),
    url(r'^price-lists/(?P<id>[0-9]+)/replace/step/1/errors$',
        price_list_replace.replace_step_1_errors,
        name='replace_step_1_errors'),
]
