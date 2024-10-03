import subprocess
import ipaddress
import requests

from requests.auth import HTTPDigestAuth
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from truegrit.models import Camera

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

    def ping_ip(self, ip):
        try:
            result = subprocess.run(
                ['ping', '-c', '1', str(ip)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE) 
            return result.returncode == 0
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
            return False
        
    def updateProperty(self, ip_address, property, value):
        text_string = "\tSetting '{}' to '{}'".format(property, value)
        print(text_string, end=' ',flush=True)
        url = "http://{}/axis-cgi/param.cgi?action=update&{}={}".format(
            ip_address,
            property,
            value
        )
        response = requests.get(url, auth=HTTPDigestAuth(username, password))
        if response.status_code == 200:
            print(f"\r{text_string} {GREEN}Success{RESET}")
        else:
            print("Something went wrong...")
            print(response.__dict__)
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

    def setup_device(self, camera):     
        ip_address = camera.ip_address
        print("Setup camera: {}".format(ip_address))
        # mac_address = self.get_attribute_from_ip(ip_address, 'root.Network.eth0.MACAddress')
        # self.save_mac_address(camera, mac_address)
        self.disableHTTPS(ip_address)
        self.updateUPnP(ip_address, camera.get_upnp_name())
        self.updateAuthMethod(ip_address)

    def configure_device(self, ip_address, upnp_name):
        self.disableHTTPS(ip_address)
        self.updateUPnP(ip_address, upnp_name)
        self.updateAuthMethod(ip_address)   

    def generate_ip_address(self, gateway, host_number):
        octets = self.get_octets(gateway)
        octets[-1] = str(host_number)
        return '.'.join(octets)          

    def get_octets(self, ip_address):
        return str(ip_address).split('.')
    
    def get_ip_addresses(self, gateway_input):
        
        host_address_input = input("\nEnter IP addresses assigned: (Ex: 43,45,47-50,88)\n").replace(" ", "")
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

    def get_camera_from_macaddress(self, gateway_input, mac_address, model_number):
        try:
            return Camera.objects.get(
                mac_address=mac_address
            )
        except ObjectDoesNotExist:      
            camera = Camera.objects.filter(
                network__gateway=gateway_input,
                model__name=model_number,
                mac_address__isnull=True
            ).first()
            self.save_mac_address(camera, mac_address)
            return camera
        

    def process_static_addresses(self, ip_addresses):
        for ip_address in ip_addresses:
            camera = Camera.objects.get(ip_address=ip_address)    
            self.configure_device(ip_address, camera.get_upnp_name()) 
            self.print_results(camera)      
        
    def process_dhcp_addresses(self, gateway_input, ip_addresses):
        for ip_address in ip_addresses:
            mac_address = self.get_attribute_from_ip(ip_address, 'root.Network.eth0.MACAddress')
            model_number = self.get_attribute_from_ip(ip_address, 'root.Brand.ProdNbr')
            camera = self.get_camera_from_macaddress(gateway_input, mac_address, model_number)
            self.configure_device(ip_address, camera.get_upnp_name())
            self.print_results(camera)
            

    def print_results(self, camera):
        if len(camera.model.name) < 9: 
            print_string = "{}\t\t{}\t{}\t{}"
        else:
            print_string = "{}\t{}\t{}\t{}"    
        print(print_string.format(camera.model.name, camera.ip_address, camera.mac_address, camera.name))

    def handle(self, *args, **options):
        # macs = [
        #     "B8A44FA9699E",
        #     "B8A44FB97727",
        #     "B8A44FA978CB",
        #     "B8A44FB5D6D2",
        #     "B8A44FB5D558"
        # ]
        # for camera in Camera.objects.filter(mac_address__in=macs):
        #     camera.ip_address = None 
        #     camera.save()
        #     print("{}\t{}\t{}\t{}".format(camera.name, camera.model.name, camera.mac_address, camera.ip_address))
        # for camera in Camera.objects.filter(ip_address="10.19.54.81"):
        #     print("{}\t{}\t{}\t{}".format(camera.name, camera.model.name, camera.mac_address, camera.ip_address))
        gateway_input = input("Enter gateway address: \n")
        static_addresses = self.get_ip_addresses(gateway_input)
        if static_addresses:
            self.process_static_addresses(static_addresses)
 
        dhcp_gateway_input = input("\nEnter DHCP gateway address ('Enter' to quit): \n")   
        dhcp_addresses = self.get_ip_addresses(dhcp_gateway_input)
        if dhcp_addresses:
            self.process_dhcp_addresses( gateway_input, dhcp_addresses)

     