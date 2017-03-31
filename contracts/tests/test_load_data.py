import pathlib
from django.core.management import call_command
from django.test import TestCase

from contracts.models import Contract

MY_DIR = pathlib.Path(__file__).resolve().parent


class LoadS70TestCase(TestCase):
    sample_filename = MY_DIR.parent / 'docs' / 'hourly_prices_sample.csv'

    def test_loads_sample(self):
        call_command(
            'load_data',
            filename=self.sample_filename
        )
        self.assertEquals(Contract.objects.count(), 79)
