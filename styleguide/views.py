from django import forms
from django.shortcuts import render

from frontend.upload import UploadWidget
from frontend.steps import StepsWidget
from data_capture.schedules.s70 import Schedule70PriceList
from . import (ajaxform_example, date_example, radio_checkbox_example,
               email_examples, storybook)


def get_degraded_upload_widget():
    class MyForm(forms.Form):
        file = forms.FileField(widget=UploadWidget(degraded=True))

    return MyForm()['file']


def get_existing_filename_upload_form():
    class MyForm(forms.Form):
        js = forms.FileField(widget=UploadWidget(
            required=False,
            existing_filename='boop.csv',
        ))
        no_js = forms.FileField(widget=UploadWidget(
            degraded=True,
            required=False,
            existing_filename='boop.csv',
        ))

    return MyForm()


def get_s70_pricelist_error_table():
    return Schedule70PriceList([
        {
            'sin': 'none',
            'labor_category': 'Button Presser',
            'education_level': 'NA',
            'min_years_experience': '1',
            'unit_of_issue': 'Hour',
            'price_including_iff': '9.0',
        },
        {
            'sin': 'none',
            'labor_category': 'Button Presser',
            'education_level': 'NA',
            'min_years_experience': 'all of them',
            'unit_of_issue': 'Hour',
            'price_including_iff': '9.0',
        }
    ]).to_error_table()


def index(request):
    ctx = {
        'storybook_url': storybook.get_url(request.META['HTTP_HOST']),
        's70_error_table': get_s70_pricelist_error_table(),
        'degraded_upload_widget': get_degraded_upload_widget(),
        'existing_filename_upload_form': get_existing_filename_upload_form(),
        'steps_widget': StepsWidget(
            labels=('Upload data', 'Validate data', 'Recover costs'),
            current=2
        )
    }
    ctx.update(ajaxform_example.create_template_context())
    ctx.update(date_example.create_template_context())
    ctx.update(radio_checkbox_example.create_template_context())
    ctx['email_examples'] = email_examples.examples

    return render(request, 'styleguide.html', ctx)
