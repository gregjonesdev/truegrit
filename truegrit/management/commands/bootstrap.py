import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from truegrit.models import (
    ProjectStatus, 
    ServerRole,
    ServerManufacturer, 
    CameraManufacturer, 
    InstallationMountType,
    InstallationStatus,
    DistributionFrameRole,
    CameraModel,
    CameraIPProcessStatus,
    VideoCompressionStandard,
    VideoQualityResolution,
)

class Command(BaseCommand):  

    def create_servermanufacturer(self, manufacturer):
        try: 
            ServerManufacturer.objects.get(name=manufacturer["name"])
        except ObjectDoesNotExist:    
            new_manufacturer = ServerManufacturer(
                name=manufacturer["name"]
            )
            new_manufacturer.set_fields_to_base()
            new_manufacturer.save()

    def get_cameramanufacturer(self, manufacturer_name):
        try: 
            return CameraManufacturer.objects.get(name=manufacturer_name)
        except ObjectDoesNotExist:    
            new_manufacturer = CameraManufacturer(
                name=manufacturer_name
            )
            new_manufacturer.set_fields_to_base()
            new_manufacturer.save()   
            return new_manufacturer     

    def create_projectstatus(self, status):
        try: 
            ProjectStatus.objects.get(name=status["name"])
        except ObjectDoesNotExist:    
            new_status = ProjectStatus(
                name=status["name"]
            )
            new_status.set_fields_to_base()
            new_status.save()

    def create_installationmounttype(self, type):
        try: 
            InstallationMountType.objects.get(name=type["name"])
        except ObjectDoesNotExist:    
            new_mounttype = InstallationMountType(
                name=type["name"]
            )
            new_mounttype.set_fields_to_base()
            new_mounttype.save()   

    def create_installationstatus(self, status):
        try: 
            InstallationStatus.objects.get(name=status["name"])
        except ObjectDoesNotExist:    
            new_mounttype = InstallationStatus(
                name=status["name"]
            )
            new_mounttype.set_fields_to_base()
            new_mounttype.save()                

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

    def create_serverrole(self, serverrole):
        try: 
            ServerRole.objects.get(name=serverrole)
        except ObjectDoesNotExist:    
            new_role = ServerRole(
                name=serverrole
            )
            new_role.set_fields_to_base()
            new_role.save()  

    def create_framerole(self, framerole):
        try: 
            DistributionFrameRole.objects.get(name=framerole["name"])
        except ObjectDoesNotExist:    
            new_role = DistributionFrameRole(
                name=framerole["name"],
                abbreviation=framerole["abbreviation"]
            )
            new_role.set_fields_to_base()
            new_role.save()  

    def create_video_compression_standard(self, standard):
        try:
            VideoCompressionStandard.objects.get(name=standard["name"])
        except ObjectDoesNotExist:
            new_standard = VideoCompressionStandard(
                name=standard["name"]
            )         
            new_standard.set_fields_to_base()
            new_standard.save()

    def create_resolution(self, resolution):
        try:
            VideoQualityResolution.objects.get(
                name=resolution["name"],
                abbreviation=resolution["abbreviation"],
                pixel_rows=resolution["pixel_rows"],
                pixel_cols=resolution["pixel_cols"],
            ) 
        except ObjectDoesNotExist:
            new_resolution = VideoQualityResolution(
                name=resolution["name"],
                abbreviation=resolution["abbreviation"],
                pixel_rows=resolution["pixel_rows"],
                pixel_cols=resolution["pixel_cols"],
            )  
            new_resolution.set_fields_to_base()
            new_resolution.save()     

    def seed_distributionframeroles(self, distributionframeroles):
        for framerole in distributionframeroles:
            self.create_framerole(framerole)        

    def seed_servermanufacturers(self, server_manufacturers):
        for manufacturer in server_manufacturers:
            self.create_servermanufacturer(manufacturer)

    def seed_cameramodels(self, camera_models):
        for model in camera_models:
            manufacturer = self.get_cameramanufacturer(model["manufacturer"])
            try: 
                CameraModel.objects.get(
                    name=model["name"],
                    manufacturer=manufacturer)
            except ObjectDoesNotExist:    
                new_model = CameraModel(
                    name=model["name"],
                    manufacturer=manufacturer
                )
                new_model.set_fields_to_base()
                new_model.save() 

    def seed_serverroles(self, server_roles):
        for role in server_roles:
            self.create_serverrole(role)  

    def seed_installationmounttypes(self, installationmounttypes):
        for type in installationmounttypes:
            self.create_installationmounttype(type)    

    def seed_installationstatus(self, installationstatus):
        for status in installationstatus:
            self.create_installationstatus(status)              

    def seed_projectstatus(self, project_status):
        print("Seeding project status..")
        for status in project_status:
            self.create_projectstatus(status)

    def seed_users(self, users):
        print("Seeding users..")
        for user in users:
            self.create_user(user)

    def seed_videocompressionstandards(self, video_compression_stds):
        for std in video_compression_stds:
            self.create_video_compression_standard(std)  

    def seed_videoqualityresolutions(self, resolutions):
        for resolution in resolutions:
            self.create_resolution(resolution)  

    def seed_camera_ip_status(self, statuses):
        for status in statuses:
            try:
                CameraIPProcessStatus.objects.get(name=status["name"])
            except ObjectDoesNotExist:
                new_status = CameraIPProcessStatus(
                    name=status["name"]
                ) 
                new_status.set_fields_to_base()
                new_status.save()                               


    def handle(self, *args, **options):
        for each in ServerRole.objects.all():
            each.delete()
        jsonData = json.loads(open('./truegrit/json/data.json').read())
        # self.seed_users(jsonData["users"])
        # self.seed_projectstatus(jsonData["project_status"])
        # self.seed_servermanufacturers(jsonData["server_manufacturers"])
        # self.seed_cameramodels(jsonData["camera_models"])
        self.seed_serverroles(jsonData["server_roles"])
        # self.seed_installationmounttypes(jsonData["installation_mounttypes"])
        # self.seed_installationstatus(jsonData["installation_status"])
        # self.seed_distributionframeroles(jsonData["distribution_frameroles"])
        # self.seed_videocompressionstandards(jsonData["video_compression_standards"])
        # self.seed_videoqualityresolutions(jsonData["video_quality_resolutions"])
        # self.seed_camera_ip_status(jsonData["camera_ip_status"])
        #video compression resolutions

