import statistics as stats
from django.core.management import BaseCommand
from price_prediction.models import LaborCategoryLookUp as LookUp

class Command(BaseCommand):

    def handle(self, *args, **options):
        labor_categories = [i for i in LookUp.objects.all() if i.labor_key]
        labor_categories = set([i.labor_key for i in labor_categories])

        counts = []
        less_than_25 = 0
        for labor_category in labor_categories:
            labor_objects = LookUp.objects.filter(labor_key=labor_category)
            if len(labor_objects) < 25:
                less_than_25 += 1
            counts.append(len(labor_objects))
        print(stats.mean(counts))
        print(stats.stdev(counts))
        print("less than 25",less_than_25)
        print("total num elements",len(counts))
