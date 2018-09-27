from django.conf.urls import include, url

from .views import (price_list_upload, bulk_upload, price_lists,
                    price_list_replace, price_list_analyze)

urlpatterns = [
    url(r'^tutorial$', price_list_upload.tutorial, name='tutorial'),
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

    url(r'^analyze/', include(price_list_analyze.steps.urls)),
    url(r'^analyze/2/errors$', price_list_analyze.analyze_step_2_errors,
        name='analyze_step_2_errors'),
    url(r'^analyze/export$', price_list_analyze.export_analysis,
        name='export_analysis'),
]
