from django.db import models
from truegrit.applib.models import CoreModel

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

class Camera(CoreModel):

    model = models.ForeignKey(
        CameraModel,
        on_delete=models.CASCADE
    )

    mac_address = models.CharField(
        max_length=12,
    )

class CameraInstallation(CoreModel):

    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE
    )    

    # ip_address

    # installation mount type

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
    pixel_cols = models.IntegerField()
    pixel_rows = models.IntegerField()           