import csv
from django.core.management.base import BaseCommand

from truegrit.models import Camera
from ipaddress import ip_address
# csv_file_path = r"C:\Users\gregoryjones\OneDrive - Preferred Technologies, LLC\Documents\My Data Sources\Devices.csv"

class Command(BaseCommand):

    


    def handle(self, *args, **options):

        bu_identifier = input("Enter business unit ID: \n")             
      

        

                                                                                    