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

class ServerManufacturer(Manufacturer):

    pass

class CameraManufacturer(Manufacturer):

    pass