from unittest import mock
from django.test import TestCase
from django.contrib.auth.models import User


class DataExplorerTests(TestCase):
    def test_logout_works(self):
        with mock.patch('django.contrib.auth.logout') as logout_mock:
            response = self.client.get('/logout/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(logout_mock.call_count, 1)
            self.assertEqual(response.status_code, 200)

    def test_dap_is_part_of_unauthenticated_requests(self):
        response = self.client.get('/')
        self.assertContains(response, 'dap.digitalgov.gov')

    def test_dap_is_not_part_of_authenticated_requests(self):
        user = User.objects.create_user('blarg')
        self.client.force_login(user)
        response = self.client.get('/')
        self.assertNotContains(response, 'dap.digitalgov.gov')
