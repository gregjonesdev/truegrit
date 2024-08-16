import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class CoreModel(models.Model):

    class Meta:
        abstract = True

    created_at = models.DateTimeField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_created_by')
    modified_at = models.DateTimeField()
    modified_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='%(app_label)s_%(class)s_modified_by')
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True)

    def set_fields_to_base(self):
        """
        This method is just a helper. When spawning new objects on the fly,
        request data isn't always available. This method is meant to set the
        created and modified attributes to some automatically available
        defaults.
        This method returns nothing. It justs sets values for the given
        instance.
        Don't abuse this. Use only when a request does not exist.
        """
        self.created_by = User.objects.earliest('pk')
        self.created_at = timezone.now()
        self.modified_by = User.objects.earliest('pk')
        self.modified_at = timezone.now()