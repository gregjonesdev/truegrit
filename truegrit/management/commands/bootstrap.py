import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

class Command(BaseCommand):  

    def seed_projectstatus(self, project_status):
        print("Seeding project status..")
        for status in project_status:
            print(status["name"])

    def handle(self, *args, **options):
        jsonData = json.loads(open('./truegrit/json/data.json').read())
        self.seed_projectstatus(jsonData["project_status"])