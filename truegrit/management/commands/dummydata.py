from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def create_cameras(self):
        for i in range(50):
            print(i)

    def handle(self, *args, **options):
        self.create_cameras()