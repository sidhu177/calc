from django.conf import settings


def get_or_create_default_site(apps):
    Site = apps.get_model("sites", "Site")
    pk = getattr(settings, 'SITE_ID', 1)
    if Site.objects.filter(pk=pk).exists():
        site = Site.objects.get(pk=pk)
    else:
        site = Site(pk=pk)
    return site


def insert_site(apps, schema_editor):
    site = get_or_create_default_site(apps)
    site.domain = 'calc.gsa.gov'
    site.name = 'CALC'
    site.save()
