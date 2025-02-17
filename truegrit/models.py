from django.db import models
from truegrit.applib.models import CoreModel
from django.contrib.auth.models import User

class ProjectStatus(CoreModel):

    name = models.CharField(
        max_length=64,
    )

class Manufacturer(CoreModel):

    class Meta:
        abstract = True 

    name = models.CharField(
        max_length=64,
    )

class ServerRole(CoreModel):

    name = models.CharField(
        max_length=64,
    )    

class InstallationMountType(CoreModel):

    name = models.CharField(
        max_length=64,
    )    
    
class InstallationStatus(CoreModel):

    name = models.CharField(
        max_length=64,
    )         

class ServerManufacturer(Manufacturer):

    pass

class CameraManufacturer(Manufacturer):

    pass

class CameraModel(CoreModel):

    manufacturer = models.ForeignKey(
        CameraManufacturer,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=64,
    )


class StoreChain(CoreModel):
    name = models.CharField(
        max_length=255, 
        unique=True
    )

class MarketArea(CoreModel):
    chain = models.ForeignKey(
        StoreChain, 
        related_name='areas', 
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=255
    )

class BusinessUnit(CoreModel):

    identifier = models.CharField(
        max_length=255,
        null=True
    )
    description = models.CharField(
        max_length=255,
        null=True
    )   
    market_area = models.ForeignKey(
        MarketArea,
        on_delete=models.CASCADE,
        null=True
    )

    marked_complete = models.BooleanField(default=False)

    def get_next_uuid(self):
        all_business_units = BusinessUnit.objects.all()
        current_index = list(all_business_units).index(self)
        return all_business_units[current_index + 1].uuid
    
    def get_previous_uuid(self):
        all_business_units = BusinessUnit.objects.all()
        current_index = list(all_business_units).index(self)
        return all_business_units[current_index - 1].uuid
    
    def is_completed(self):
        if self.marked_complete:
            return True
        for camera in Camera.objects.filter(network__business_unit=self):
            if camera.mac_address:
                return True

    def camera_count(self):
        return Camera.objects.filter(network__business_unit=self).count()             


class Network(CoreModel):

    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        null=True
    )
    subnet = models.GenericIPAddressField(
        protocol='IPv4',
        null=True)
    gateway = models.GenericIPAddressField(
        protocol='IPv4',
        null=True)

class IPDevice(CoreModel):

    class Meta:
        abstract = True 

    mac_address = models.CharField(
        max_length=12,
        null=True
    ) 

    network = models.ForeignKey(
        Network,
        on_delete=models.CASCADE,
        null=True
    )
    ip_address = models.GenericIPAddressField(
        protocol='IPv4', 
        blank=True, 
        null=True)


class Camera(IPDevice):

    model = models.ForeignKey(
        CameraModel,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=255,
        null=True
    ) 

    def get_upnp_name(self):
        return "{}-{}".format(
            self.network.business_unit.identifier,
            self.name)                 

class CameraIPProcessStatus(CoreModel):

    name = models.CharField(
        max_length=64,
    )


class CameraIPProcess(CoreModel):

    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE
    ) 
    status = models.ForeignKey(
        CameraIPProcessStatus,
        on_delete=models.CASCADE
    )  
    comment = models.CharField(
        max_length=255,
    )    



class DistributionFrameRole(CoreModel):

    name = models.CharField(
        max_length=64,
    ) 
    abbreviation = models.CharField(
        max_length=64,
    )  

class DistributionFrame(CoreModel):

    number = models.CharField(
        max_length=8,
    )  
    role = models.ForeignKey(
        DistributionFrameRole,
        on_delete=models.CASCADE
    )     


class VideoCompressionStandard(CoreModel):

    name = models.CharField(
        max_length=64,
    )     

class VideoQualityResolution(CoreModel):

    name = models.CharField(
        max_length=64,
        null=True
    )
    abbreviation = models.CharField(
        max_length=16,
        null=True
    )  
    pixel_cols = models.IntegerField()
    pixel_rows = models.IntegerField()   


class UserSettings(CoreModel):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dark_mode = models.BooleanField(default=False)


class Project(CoreModel):

    number = models.CharField(
        max_length=255,
        null=True
    )
    description = models.CharField(
        max_length=255,
        null=True
    )
    status = models.ForeignKey(
        ProjectStatus,
        related_name='status',
        on_delete=models.CASCADE,
        )

    def get_prefixed_number(self):    
        if self.number and self.number[:6].isdigit():
            return "PJT{}".format(self.number)
        else:
            return self.number

    def get_title(self):
        if self.number:
            prefixed_number = self.get_prefixed_number()
            if self.description:
                return "{}: {}".format(prefixed_number, self.description[:20])
            else:
                return prefixed_number    
        else:
            return self.description[:25]    
            


    def get_daily_hours(self, target_date):
        hours = 0
        for entry in self.timeentry_set.filter(start_time__date=target_date):
            hours += entry.get_duration()
        return hours    
            
    
class TimeEntry(CoreModel):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        null=True) 

    def get_duration(self):
        if self.end_time and self.start_time:
            time_difference = self.end_time - self.start_time
            # Convert difference to hours
            hours = time_difference.total_seconds() / 3600
            # Round to the nearest 0.25 hour
            return round(hours * 4) / 4
        return 0    
    

class SubTask(CoreModel):
    time_entry = models.ForeignKey(
        TimeEntry, 
        on_delete=models.CASCADE)
    description = models.CharField(
        max_length=255
    )

class Server(IPDevice):

    description = models.CharField(
        max_length=255
    )
    location = models.CharField(
        max_length=255
    )
    hostname = models.CharField(
        max_length=255
    )
    alias = models.CharField(
        max_length=255
    )
    serial_number = models.CharField(
        max_length=255
    )
    # windows activation key
    # windows username
    # windows password
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE)
    # warranty expiration

    pass


class ServerRoleAssignment(CoreModel):

    server = models.ForeignKey(
        Server,
        on_delete=models.CASCADE
    )   
    role = models.ForeignKey(
        ServerRole,
        on_delete=models.CASCADE
    )   

class VPNGateway(CoreModel):

    subdomain = models.CharField(
        max_length=255
    )
    username = models.CharField(
        max_length=255
    )


class Person(CoreModel):

    first_name = models.CharField(
        max_length=255
    )
    last_name = models.CharField(
        max_length=255
    ) 

class Company(CoreModel):

    name = models.CharField(
        max_length=255
    )


class Employee(CoreModel):

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE
    )  
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )  
    email = models.EmailField(unique=True)      

class StreamUsage(CoreModel):

    name = models.CharField(
        max_length=64
    )

class StreamResolutionDescription(CoreModel):

    name = models.CharField(
        max_length=64
    )    


class StreamSettings(CoreModel):

    usage = models.ForeignKey(
        StreamUsage,
        on_delete=models.CASCADE
    )   
    resolution_description = models.ForeignKey(
        StreamResolutionDescription,
        on_delete=models.CASCADE,
        null=True
    )   
    resolution = models.ForeignKey(
        VideoQualityResolution,
        on_delete=models.CASCADE,
        null=True
    )
    framerate = models.IntegerField()
    image_quality = models.IntegerField()
    keyframe_interval = models.IntegerField()


class SchoolDistrict(CoreModel):

    name = models.CharField(
        max_length=255
    )
    acronym = models.CharField(
        max_length=64
    )

class School(CoreModel):

    name = models.CharField(
        max_length=255
    )
    acronym = models.CharField(
        max_length=64
    )    
    district = models.ForeignKey(
        SchoolDistrict,
        on_delete=models.CASCADE
    )