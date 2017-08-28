import os
from unittest import TestCase
import json
import yaml

from semantic_version import Version
from django.conf import settings

MY_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.normpath(os.path.join(MY_DIR, '..', '..'))


def path(*x):
    return os.path.join(ROOT_DIR, *x)


class PythonVersionTests(TestCase):
    '''
    Ensure all our configuration files, documentation, etc. specify the
    same Python version.
    '''

    version = Version('3.6.2')

    def test_runtime_txt(self):
        with open(path('runtime.txt')) as f:
            self.assertEqual(f.read().strip(),
                             'python-{}'.format(self.version))

    def test_dockerfile(self):
        with open(path('Dockerfile')) as f:
            self.assertIn('FROM python:{}'.format(self.version),
                          f.read())

    def test_circle_yml(self):
        with open(path('.circleci/config.yml')) as f:
            data = yaml.safe_load(f)
            # In CircleCI we can only specify down to the minor number
            self.assertEqual(
                str(data['jobs']['build']['docker'][0]['image']),
                f"circleci/python:{self.version.major}.{self.version.minor}")

    def test_docs_setup_md(self):
        with open(path('docs', 'setup.md')) as f:
            self.assertIn(f'Python {self.version}', f.read())


class PostgresVersionTests(TestCase):

    version = Version(settings.POSTGRES_VERSION)

    def test_docs_setup_md(self):
        with open(path('docs', 'setup.md')) as f:
            self.assertIn(
                f'Postgres {self.version.major}.{self.version.minor}',
                f.read())

    def test_docker_compose_yml(self):
        with open(path('docker-compose.yml')) as f:
            self.assertIn(f"image: postgres:{self.version}", f.read())

    def test_circle_yml(self):
        with open(path('.circleci/config.yml')) as f:
            data = yaml.safe_load(f)
            # In Circle we can only specify down to the minor number
            self.assertEqual(
                str(data['jobs']['build']['docker'][1]['image']),
                f"circleci/postgres:{self.version.major}.{self.version.minor}")


class NodeVersionTests(TestCase):
    '''
    Ensure all our configuration files, documentation, etc. specify
    the same Node version.
    '''

    version = Version('6.0', partial=True)

    def test_package_json(self):
        with open(path('package.json')) as f:
            package = json.load(f)
            min_version = package['engines']['node'].split()[0]
            self.assertEqual(min_version, f'>={self.version}')

    def test_docs_setup_md(self):
        with open(path('docs', 'setup.md')) as f:
            self.assertIn(f'Node {self.version}', f.read())
