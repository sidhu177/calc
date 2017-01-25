from django.apps import apps
from django.test import TestCase, override_settings
from django.contrib.sites.models import Site

from ..migrations._util_0001 import insert_site


class SiteTests(TestCase):
    def test_default_site_is_set_by_migration(self):
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
