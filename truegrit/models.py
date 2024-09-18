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


class Network(CoreModel):

    subnet = models.GenericIPAddressField(protocol='IPv4')
    gateway = models.GenericIPAddressField(protocol='IPv4')


class Camera(CoreModel):

    model = models.ForeignKey(
        CameraModel,
        on_delete=models.CASCADE
    )
    mac_address = models.CharField(
        max_length=12,
        null=True
    ) 
    network = models.ForeignKey(
        Network,
        on_delete=models.CASCADE,
        null=True
    )
    ip_address = models.GenericIPAddressField(protocol='IPv4', blank=True, null=True)
    name = models.CharField(
        max_length=255,
        null=True
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
        max_length=255
    )

class Project(CoreModel):

    number = models.IntegerField()
    description = models.CharField(
        max_length=255,
        null=True
    )
    status = models.ForeignKey(
        ProjectStatus,
        related_name='status',
        on_delete=models.CASCADE,
        )
    