from django.db import models
from truegrit.applib.models import CoreModel

class ProjectStatus(CoreModel):

    name = models.CharField(
        max_length=64,
    )