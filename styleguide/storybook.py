import os


STORYBOOK_PORT = os.environ.get('STORYBOOK_PORT', '')


def get_url(host: str) -> str:
    if STORYBOOK_PORT:
        if ':' in host:
            host = host.split(':')[0]
        return 'http://{}:{}/'.format(host, STORYBOOK_PORT)
    return '/storybook/'
