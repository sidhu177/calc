from django.test import TestCase
from django.contrib.sites.models import Site


class SiteTests(TestCase):
    def test_default_site_is_created(self):
        # According to the Django sites framework documentation,
        # django.contrib.sites registers a post_migrate signal handler
        # which creates a default site named example.com with the
        # domain example.com. This just verifies that behavior.

        site = Site.objects.get_current()
        self.assertEqual(site.domain, 'example.com')
        self.assertEqual(site.name, 'example.com')
