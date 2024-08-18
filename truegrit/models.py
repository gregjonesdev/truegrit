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