from django.apps import apps
from django.test import TestCase, override_settings
from django.contrib.sites.models import Site
from django.core.management import call_command

from ..migrations._util_0002 import insert_site


class SiteTests(TestCase):
    def test_default_site_is_set_by_migration(self):
        # We need to fake-migrate back and apply our migration that
        # inserts the site, or else any TransactionTestCases that
        # ran before us will screw up this test, for some reason. SO WEIRD.
        call_command('migrate', 'meta', '0001_initial', '--fake')
        call_command('migrate', 'meta', '0002_insert_site')

        site = Site.objects.get_current()
        self.assertEqual(site.domain, 'calc.gsa.gov')
        self.assertEqual(site.name, 'CALC')


class InsertSiteTests(TestCase):
    def test_it_creates_default_site_if_it_does_not_exist(self):
        with override_settings(SITE_ID=152):
            insert_site(apps, None)

        site = Site.objects.get(pk=152)
        self.assertEqual(site.name, 'CALC')
        self.assertEqual(site.domain, 'calc.gsa.gov')

    def test_it_uses_default_site_if_it_exists(self):
        site = Site(pk=157, name="boop", domain="boop.com")
        site.save()

        with override_settings(SITE_ID=157):
            insert_site(apps, None)

        site.refresh_from_db()
        self.assertEqual(site.name, 'CALC')
        self.assertEqual(site.domain, 'calc.gsa.gov')
