import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

class Command(BaseCommand):  

    def handle(self, *args, **options):
        print("hello")