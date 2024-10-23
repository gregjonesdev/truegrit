import subprocess
import ipaddress
import requests
import re
import os
import platform
from requests.auth import HTTPDigestAuth
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from truegrit.models import Camera, Network

username = 'root'
password = 'h3bc4m3r4'

GREEN = '\033[92m'
RESET = '\033[0m'

ignore_host_numbers = (1,2)

handy_url = "http://10.10.0.2/axis-cgi/param.cgi?action=list"

class Command(BaseCommand):  

    def is_valid_ipv4(self, address):
        try:
            ipaddress.IPv4Address(address)
            return True 
        except:
            return False

    def is_online(self, ip):
        try:
            result = subprocess.run(
                ['ping', '-c', '1', str(ip)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE) 
            return result.returncode == 0
        except Exception as e:
            return False
        
    def updateProperty(self, ip_address, property, value):
        text_string = "Set '{}' to '{}'".format(property.replace("root.",""), value)
        url = "http://{}/axis-cgi/param.cgi?action=update&{}={}".format(
            ip_address,
            property,
            value
        )
        response = requests.get(url, auth=HTTPDigestAuth(username, password))
        checkmark = '\u2713'
        if response.status_code == 200:
            print(f"\t\t{GREEN}{checkmark}{RESET} {text_string}")
        else:
            print("Something went wrong...")
            error_pattern = r'<p>(.*?)</p>'
            string_response = str(response._content).replace("\\n", " ").replace("\\", "")
            error_message = re.search(error_pattern, string_response)
            print(error_message.group(1))
            raise SystemExit(0)

        
    def listdefinitions(self):
        pass
        #works
        #http://10.10.0.2/axis-cgi/param.cgi?action=listdefinitions&group=root.Brand.ProdFullName&listformat=xmlschema

    def get_attribute_string(self, ip_address, value_name):
        # works
        url = "http://{}/axis-cgi/param.cgi?action=list&group={}".format(ip_address, value_name)    
        response = requests.get(url, auth=HTTPDigestAuth(username, password))
        return response.content

    def get_attribute_from_ip(self, ip_address, attribute_name):
        attribute_string = str(self.get_attribute_string(
            ip_address,
            attribute_name))
        return self.extract_value(attribute_string)

    def save_mac_address(self, camera, mac_address):  
        # text_string = "\tSetting {} to '{}'".format("MAC address", mac_address)
        # print(text_string, end=' ',flush=True)
        camera.mac_address = mac_address
        camera.save()
        # print(f"\r{text_string} {GREEN}Success{RESET}")
    
    def updateAuthMethod(self, ip_address):
         # Turn off 802.1 authentication:
        self.updateProperty(ip_address, "root.Network.Interface.I0.dot1x.Enabled", "no")

    def extract_value(self, input_string):
        parts = input_string.split('=') 
        if len(parts) > 1:
            value = parts[1] 
            return value.split("\\")[0].strip().replace(":", "")
        
    def disableHTTPS(self, ip_address):
        self.updateProperty(ip_address, "root.HTTPS.Enable", "no")
        self.updateProperty(ip_address, "root.System.BoaGroupPolicy.admin", "http")
        
    def updateUPnP(self, ip_address, upnp_name):
        self.updateProperty(ip_address, "root.Network.UPnP.FriendlyName", upnp_name)

    def configure_device(self, ip_address, upnp_name):
        print("\n\t{}: {}".format(ip_address, upnp_name))
        self.disableHTTPS(ip_address)
        self.updateUPnP(ip_address, upnp_name)
        self.updateAuthMethod(ip_address)   

    def generate_ip_address(self, gateway, host_number):
        octets = self.get_octets(gateway)
        octets[-1] = str(host_number)
        return '.'.join(octets)          

    def get_octets(self, ip_address):
        return str(ip_address).split('.')
    
    def get_ip_addresses(self, gateway_input, type):
        prompt_string = "\nEnter {} IP addresses assigned: (Ex: 43,45,47-50,88).\n".format(type)
        host_address_input = input(prompt_string).replace(" ", "")
        if host_address_input:
            host_addresses = []
            for host_number in host_address_input.split(","):
                ip_range = host_number.split("-")
                ip_start = int(ip_range[0])
                if len(ip_range) > 1:
                    ip_end = int(ip_range[1]) + 1
                else:
                    ip_end = int(ip_start) + 1
                for each in range(ip_start, ip_end):
                    ip_address = self.generate_ip_address(gateway_input, each)
                    if self.is_valid_ipv4(ip_address):
                        host_addresses.append(ip_address)
            return host_addresses

    def get_camera_from_macaddress(self, network, mac_address, model_number):
        try:
            return Camera.objects.get(
                mac_address=mac_address
            )
        except ObjectDoesNotExist:      
            camera = Camera.objects.filter(
                network=network,
                model__name=model_number,
                ip_address__isnull=True,
                mac_address__isnull=True
            ).order_by("name").first()
            self.save_mac_address(camera, mac_address)
            return camera        
  
    
    def get_network_from_gateway(self, gateway):
        return Network.objects.get(gateway=gateway)
    
    def get_network_from_bu(self, bu_identifier):
        return Network.objects.get(business_unit__identifier=bu_identifier)

    def handle_static(self):
        gateway_input = input("Enter gateway address: \n")   
        static_addresses = self.get_ip_addresses(gateway_input, "Static")

        if static_addresses:   
            results = []
            for ip_address in static_addresses:
                try:
                    camera = Camera.objects.get(ip_address=ip_address)
                except ObjectDoesNotExist:
                    camera = None 
                if camera:       
                    mac_address = self.get_attribute_from_ip(ip_address, 'root.Network.eth0.MACAddress')
                    default_router = self.get_attribute_from_ip(ip_address, 'root.Network.DefaultRouter')
                    gateway = self.get_attribute_from_ip(ip_address, 'root.Network.eth0.SubnetMask')
                    self.save_mac_address(camera, mac_address)
               
                    results.append(self.build_result_row(camera, default_router, gateway))   
                    self.configure_device(ip_address, camera.get_upnp_name()) 
            self.print_status(results)
        

    def build_result_row(self, camera, default_router, gateway):
        ip_to_print = camera.ip_address if camera.ip_address else "[DHCP]"
        return (camera.model.name, camera.mac_address, camera.name, ip_to_print, default_router, gateway)
            

    def print_status(self, results):
        print("\n")
        for result in results:
            if not result[0] == "offline":
                print("{:<15} {:<15} {:<50} {:<10} {:<10} {:<10}".format(*result))
        print("\n")
        for result in results:
            if result[0] == "offline":
                print("Unable to connect to {}.".format(result[1]))    


    def get_network_for_dhcp(self):
        while True:
            ip_protocol = input("\nFind availabe cameras by: \n\t[1] Business Unit \n\t[2] Gateway\n")   
            if ip_protocol == "1":
                bu_input = input("\nEnter Business Unit:\n")  
                return self.get_network_from_bu(bu_input)
            elif ip_protocol == "2":
                gateway_input = input("Enter Default Gateway:\n")
                return self.get_network_from_gateway(gateway_input)
            else:  
                print("Input not recognized. Please try again.\n") 


    def handle_dhcp(self):
        network = self.get_network_for_dhcp()
        results = []
        for ip_address in self.get_ip_addresses("10.10.1.1", "DHCP"):
            if self.is_online(ip_address):
                model_number = self.get_attribute_from_ip(ip_address, 'root.Brand.ProdNbr')
                mac_address = self.get_attribute_from_ip(ip_address, 'root.Network.eth0.MACAddress')
                default_router = self.get_attribute_from_ip(ip_address, 'root.Network.DefaultRouter')
                gateway = self.get_attribute_from_ip(ip_address, 'root.Network.eth0.SubnetMask')
                camera = self.get_camera_from_macaddress(network, mac_address, model_number)
                results.append(self.build_result_row(camera, default_router, gateway))
                self.configure_device(ip_address, camera.get_upnp_name())
            else:
                results.append(("offline", ip_address))    
        self.print_status(results) 

    def clear_screen(self):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
                
             
    def handle(self, *args, **options):
        self.clear_screen()   
        # for camera in Camera.objects.filter(network__gateway='172.20.68.1'):
            
        #     print(camera.created_at)
        #     camera.delete()

        # #     camera.ip_address = None
        # #     camera.mac_address = None 
        # #     camera.save()
        # raise SystemExit(0)
      
        # dhcp_addresses = self.get_ip_addresses("10.10.0.1", "DHCP")
        # if dhcp_addresses:
        #     bu_identifier = input("Enter Business Unit identifier: \n")
        #     self.process_dhcp_addresses(bu_identifier, dhcp_addresses)

        while True:
            ip_protocol = input("Please select the type of IP addresses to process: \n\t[1] Static \n\t[2] DHCP\n")   
            if ip_protocol == "1":
                self.handle_static()
                break
            elif ip_protocol == "2":
                self.handle_dhcp()
                break
            else:  
                print("Input not recognized. Please try again.\n")


        print("\n")

     