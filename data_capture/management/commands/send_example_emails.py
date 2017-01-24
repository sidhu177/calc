from django.utils import timezone

import djclick as click
from django.template.loader import render_to_string

from data_capture import email


@click.command()
@click.argument('to', default='user@example.com')
def command(to):
    '''
    Send examples of all the email templates in the Data Capture application.
    '''

    pl_ctx = {
        'price_list': {
            'created_at': timezone.now(),
            'contract_number': 'GS-12-Example',
            'get_schedule_title': 'Fake Schedule',
            'vendor_name': 'Example Vendor, Inc.',
        },
        'details_link': 'https://example.com/price-list/details',
    }

    email.send_mail(
        subject='Example Price List Approved',
        to=[to],
        html_message=render_to_string(
            'data_capture/email/price_list_approved.html',
            pl_ctx))

    email.send_mail(
        subject='Example Price List Rejected',
        to=[to],
        html_message=render_to_string(
            'data_capture/email/price_list_rejected.html',
            pl_ctx))

    email.send_mail(
        subject='Example Price List Retired',
        to=[to],
        html_message=render_to_string(
            'data_capture/email/price_list_retired.html',
            pl_ctx))

    email.send_mail(
        subject='Example Bulk Upload Succeeded',
        to=[to],
        html_message=render_to_string(
            'data_capture/email/bulk_upload_succeeded.html',
            {
                'upload_source': {
                    'id': 2,
                    'submitter': {'email': 'example_admin@example.com'},
                    'created_at': timezone.now(),
                },
                'num_contracts': 50123,
                'num_bad_rows': 25,
            }))

    email.send_mail(
        subject='Example Bulk Upload Failed',
        to=[to],
        html_message=render_to_string(
            'data_capture/email/bulk_upload_failed.html',
            {
                'upload_source': {
                    'id': 2,
                    'submitter': {'email': 'example_admin@example.com'},
                    'created_at': timezone.now(),
                },
                'r10_upload_link': 'https://example.com/r10_bulk_upload',
                'traceback': 'error traceback'
            }))

    email.send_mail(
        subject='Example Price List Review Reminder',
        to=[to],
        html_message=render_to_string(
            'data_capture/email/approval_reminder.html',
            {
                'count_unreviewed': 20,
                'unreviewed_url': 'https://example.com/unreviewed_price_lists',
            }))
