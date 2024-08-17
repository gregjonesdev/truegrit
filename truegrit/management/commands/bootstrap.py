import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from truegrit.models import ProjectStatus

class Command(BaseCommand):  

    def create_projectstatus(self, status):
        try: 
            ProjectStatus.objects.get(name=status["name"])
        except ObjectDoesNotExist:    
            new_status = ProjectStatus(
                name=status["name"]
            )
            new_status.set_fields_to_base()
            new_status.save()

    def create_user(self, user):
        try:
            user = User.objects.get(username=user["username"])
        except ObjectDoesNotExist:
            user = User(
                is_superuser=user["is_superuser"],
                username=user["username"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                is_active=user["is_active"],
            )
            user.save()      

    def seed_projectstatus(self, project_status):
        print("Seeding project status..")
        for status in project_status:
            self.create_projectstatus(status)

    def seed_users(self, users):
        print("Seeding users..")
        for user in users:
            print(user)
            self.create_user(user)        


    def handle(self, *args, **options):
        jsonData = json.loads(open('./truegrit/json/data.json').read())
        self.seed_users(jsonData["users"])
        self.seed_projectstatus(jsonData["project_status"])