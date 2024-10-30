import csv
from django.core.management.base import BaseCommand

from truegrit.models import Camera

# csv_file_path = r"C:\Users\gregoryjones\OneDrive - Preferred Technologies, LLC\Documents\My Data Sources\Devices.csv"

class Command(BaseCommand):

    def ip_ranges(self, ip_list):
        # Sort IPs numerically
        ip_list = sorted(ip_list, key=lambda ip: int(ip_address(ip)))
        
        ranges = []
        start = ip_list[0]
        end = start

        for i in range(1, len(ip_list)):
            current_ip = ip_list[i]
            previous_ip = ip_list[i - 1]
            
            # Check if the current IP is consecutive with the previous IP
            if int(ip_address(current_ip)) == int(ip_address(previous_ip)) + 1:
                end = current_ip  # Update the end of the current range
            else:
                # Append range to the list
                if start == end:
                    ranges.append(start)
                else:
                    ranges.append(f"{start}-{end}")
                # Start a new range
                start = current_ip
                end = current_ip

        # Append the final range
        if start == end:
            ranges.append(start)
        else:
            ranges.append(f"{start}-{end}")

        return ranges  

    def get_network_from_bu(self, bu_identifier):
        return Network.objects.get(business_unit__identifier=bu_identifier)    


    def handle(self, *args, **options):

        bu_identifier = input("Enter business unit ID: \n")             
        # network = self.get_network_from_bu(bu_identifier)

        unassigned_cameras = {}

        for camera in Camera.objects.filter(
            network__business_unit__identifier=bu_identifier,
            mac_address__isnull=True):
            if not camera.model.name in unassigned_cameras.keys():
                unassigned_cameras[camera.model.name] = []

        print(unassigned_cameras)        

                                                                                    