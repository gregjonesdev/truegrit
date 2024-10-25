import os
import csv
import platform
import requests

from openpyxl import load_workbook
from requests.auth import HTTPDigestAuth
from django.core.management.base import BaseCommand

from truegrit.models import Network, Camera


username = 'root'
password = 'h3bc4m3r4'

# Define file paths
csv_file_path = r"C:\Users\gregoryjones\OneDrive - Preferred Technologies, LLC\Documents\My Data Sources\Devices.csv"
excel_file_path = r"C:\Users\gregoryjones\OneDrive - Preferred Technologies, LLC\Book3.xlsx"

# List to store tuples
class Command(BaseCommand):  

    def clear_screen(self):
        # move this to common file
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    def get_network_from_bu(self, bu_identifier):
        return Network.objects.get(business_unit__identifier=bu_identifier)


    def get_attribute_string(self, ip_address, value_name):
        # works
        url = "http://{}/axis-cgi/param.cgi?action=list&group={}".format(ip_address, value_name)
        try:    
            response = requests.get(url, auth=HTTPDigestAuth(username, password))
            return response.content
        except requests.exceptions.ConnectionError:
            print("Unable to connect to {}".format(ip_address))

    def get_attribute_from_ip(self, ip_address, attribute_name):
        attribute_string = str(self.get_attribute_string(
            ip_address,
            attribute_name))
        return self.extract_value(attribute_string)

    def extract_value(self, input_string):
        parts = input_string.split('=') 
        if len(parts) > 1:
            value = parts[1] 
            return value.split("\\")[0].strip().replace(":", "")    

    def is_dhcp(self, ip_address):
        return self.get_attribute_from_ip(ip_address, 'root.Network.Resolver.ObtainFromDHCP')  


    def get_firmware_version(self, ip_address):
        return self.get_attribute_from_ip(ip_address, 'root.Properties.Firmware.Version') 

    def get_dhcp_camera(self, network, model_number):
        return Camera.objects.filter(
                network=network,
                model__name=model_number,
                ip_address__isnull=True,
                mac_address__isnull=True
            ).order_by("name").first()                 

    def get_camera(self, ip_address, network):

        is_dhcp = self.is_dhcp(ip_address)
        if is_dhcp == "no":
            return Camera.objects.get(
                ip_address=ip_address,
                network=network)     
        else:
            model_number = self.get_attribute_from_ip(ip_address, 'root.Brand.ProdNbr')
            return self.get_dhcp_camera(network, model_number)
            


    def update_xls(self, sheet, ip_address, firmware_version, is_dot1x_disabled, mac_address):        
        for excel_row in sheet.iter_rows(min_row=2, max_col=11, values_only=False):  # Adjust min_row if there's a header
            cell_f = excel_row[5]  # Column F is the 6th column in zero-based index

            if cell_f.value == ip_address:  # Check if the value in F matches the extracted value
                # Assign values to columns K and J (10th and 9th columns)
                excel_row[10].value = row[0]  # Column K mac address
                excel_row[8].value = row[4]   # Column I firmware
                break  # Exit after finding the match
        

    def disableHTTPS(self, ip_address):
        self.updateProperty(ip_address, "root.HTTPS.Enable", "no")
        self.updateProperty(ip_address, "root.System.BoaGroupPolicy.admin", "http")
        
    def updateUPnP(self, ip_address, upnp_name):
        self.updateProperty(ip_address, "root.Network.UPnP.FriendlyName", upnp_name)

    def updateAuthMethod(self, ip_address):
         # Turn off 802.1 authentication:
        self.updateProperty(ip_address, "root.Network.Interface.I0.dot1x.Enabled", "no")    

    def configure_device(self, ip_address, upnp_name):
        print("\n\t{}: {}".format(ip_address, upnp_name))
        self.disableHTTPS(ip_address)
        self.updateUPnP(ip_address, upnp_name)
        self.updateAuthMethod(ip_address)   

    def is_dot1x_disabled(self, ip_address):
        # 
        is_dot1x_enabled = self.get_attribute_from_ip(ip_address, 'root.Network.Interface.I0.dot1x.Enabled')
        if is_dot1x_enabled == "no":
            return "Yes"
        elif is_dot1x_enabled == "yes":
            return ""              

    def save_mac_address(self, camera, mac_address):
        camera.mac_address = mac_address 
        camera.save()

        

    def handle(self, *args, **options):
        self.clear_screen() 
        bu_identifier = input("Enter business unit ID: \n")             
        network = self.get_network_from_bu(bu_identifier)
        # Load the workbook and select the specific sheet
        wb = load_workbook(excel_file_path)
        sheet = wb[bu_identifier]

        
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)

            #skip first row
            next(csv_reader)

            for row in csv_reader:
                # Extract substring from row[2] before the ":"
                ip_address = row[2].split(":")[0]
                mac_address = row[0]
                firmware_version = row[4]
                
                camera = self.get_camera(ip_address, network)
                print(camera)
                raise SystemExit(0)
                self.save_mac_address(camera, mac_address)
                self.configure_device(ip_address, camera.get_upnp_name()) 
                is_dot1x_disabled = self.is_dot1x_disabled(ip_address)
                  
                # Iterate through rows in Excel sheet to find the match in column F (6th column, 1-indexed)
                self.update_xls(
                    sheet, 
                    ip_address, 
                    firmware_version, 
                    is_dot1x_disabled, 
                    mac_address)

        # Save the modified workbook
        wb.save(excel_file_path)
        print("Excel file updated successfully.")