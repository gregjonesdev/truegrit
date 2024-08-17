import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from truegrit.models import ProjectStatus

class Command(BaseCommand):  

    def create_servermanufacturer(self, manufacturer):
        try: 
            ServerManufacturer.objects.get(name=manufacturer["name"])
        except ObjectDoesNotExist:    
            new_manufacturer = ProjectStatus(
                name=manufacturer["name"]
            )
            new_manufacturer.set_fields_to_base()
            new_manufacturer.save()

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

    # def seed_servermanufacturers(self, server_manufacturers):
    #     for manufacturer in server_manufacturers:
    #         self.create_servermanufacturer(manufacturer)

    # def seed_cameramanufacturers(self, camera_manufacturers):
    #     for manufacturer in camera_manufacturers:
    #         self.create_cameramanufacturer(manufacturer)

    # def seed_serverroles(self, server_roles):
    #     for role in server_roles:
    #         self.create_serverrole(role)  

    # def seed_installationmounttypes(self, installationmounttypes):
    #     for type in installationmounttypes:
    #         self.create_installationmounttype(type)       

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
        # self.seed_servermanufacturers(jsonData["server_manufacturers"])
        # self.seed_cameramanufacturers(jsonData["camera_manufacturers"])
        # self.seed_serverroles(jsonData["server_roles"])
        # self.seed_installationmounttypes(jsonData["installation_mounttypes"])
