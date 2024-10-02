import subprocess
import ipaddress
import requests

from requests.auth import HTTPDigestAuth
from django.core.management.base import BaseCommand
from truegrit.models import Camera, Network

username = 'root'
password = 'h3bc4m3r4'

GREEN = '\033[92m'
RESET = '\033[0m'

ignore_host_numbers = (1,2)

handy_url = "http://10.10.0.2/axis-cgi/param.cgi?action=list"

class Command(BaseCommand):  

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

    def save_mac_address(self, camera, mac_address):
        camera.mac_address = mac_address
        camera.save()
    
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

    def get_discovered_models(self, network_list):
        discovered_models = {}
        for network in network_list:
            camera_host_numbers = network["camera_host_numbers"]
            current_host_number = camera_host_numbers[0]
            gateway = network["number"]
            while current_host_number <= camera_host_numbers[1]:
                ip_address = self.generate_ip_address(gateway, current_host_number)
                current_host_number += 1
                if self.is_online_camera(ip_address):
                    mac_address_string = str(self.get_attribute_string(
                        ip_address,
                        'root.Network.eth0.MACAddress'))
                    mac_address = self.extract_value(mac_address_string)
                    model_number_string = str(self.get_attribute_string(
                        ip_address,
                        'root.Brand.ProdNbr'))
                    model_number = self.extract_value(model_number_string)
                    if not model_number in discovered_models.keys():
                        discovered_models[model_number] = []
                    discovered_models[model_number].append((mac_address, ip_address))    
        return discovered_models            

    def is_online_camera(self, ip_address):
        # return self.is_not_gateway(ip_address) and self.ping_ip(ip_address)    
        return self.is_not_gateway(ip_address)

    def setup_device(self, camera, device_ip):
        
        ip_address = camera.ip_address
        # print("Current ip: {}".format(device_ip))
        print("Setup camera: {}".format(ip_address))
        
        self.disableHTTPS(ip_address)
        self.updateUPnP(ip_address, camera.get_upnp_name())
        self.updateAuthMethod(ip_address)


    def generate_ip_address(self, gateway, host_number):
        octets = self.get_octets(gateway)
        octets[-1] = str(host_number)
        return '.'.join(octets)          
    
    def is_not_gateway(self, ip_address):
        octets = self.get_octets(ip_address)
        last_octet = self.get_last_octet(octets)
        print(int(last_octet))
        return int(last_octet) not in ignore_host_numbers
    
    def get_last_octet(self, octets):
        return octets[-1]

    def get_octets(self, ip_address):
        return str(ip_address).split('.')


    def handle(self, *args, **options):

        store_network = "10.19.54.1"
        completed = [
            "10.19.54.100",
            "10.19.54.101",
            "10.19.54.102",
            "10.19.54.103",
            "10.19.54.104",
            "10.19.54.105",
            "10.19.54.106",
            "10.19.54.107",
            "10.19.54.108",
            "10.19.54.12",
            "10.19.54.14",
            "10.19.54.153",
            "10.19.54.157",
            "10.19.54.159",
            "10.19.54.162",
            "10.19.54.165",
            "10.19.54.168",

        ]
        # cameras = Camera.objects.filter(network__gateway=gateway)
        # for camera in cameras:
        #     # print(camera.ip_address)
        #     if self.ping_ip(camera.ip_address):
        #         self.setup_device(camera.ip_address)

        # host_numbers = [
        #     14, 153, 157, 159, 162, 168
        # ]
        # for host_number in host_numbers:
        #     ip_address = self.generate_ip_address(gateway, host_number)
        #     camera = Camera.objects.get(ip_address=ip_address)
        #     self.setup_device(camera)
        # camera_count = 1
        # cameras_found = self.scan_cameras(camera_count)
        # print(cameras_found)
        gateway_input = input("Enter gateway address: \n")
        host_address_input = input("\nEnter IP addresses assigned: (Ex: 43,45,47-50,88)\n")
        host_addresses = []
        for host_number in host_address_input.split(","):
            if "-" in host_number:
                ip_range = host_number.split("-")
                
                ip_start = int(ip_range[0])
                ip_end = int(ip_range[1]) +1
                for each in range(ip_start, ip_end):
                    ip_address = self.generate_ip_address(gateway_input, each)
                    host_addresses.append(ip_address)
            else:
                ip_address = self.generate_ip_address(gateway_input, host_number)
                host_addresses.append(ip_address)
        print(host_addresses)        
        raise SystemExit(0)
        

        network_list = [
            {
                "number": "10.19.54.1",
                "camera_host_numbers": (20, 27)
            },
        ]

        discovered_models = self.get_discovered_models(network_list)
        print(discovered_models)
        network = Network.objects.get(gateway=store_network)

        for model_name in discovered_models:
            model_count = len(discovered_models[model_name])
            new_cameras = Camera.objects.filter(
                network=network,
                model__name=model_name,
                ip_address__isnull=False,
            ).exclude(ip_address__in=completed).order_by('ip_address')[:model_count]

            index = 0
            while index < len(new_cameras):
                new_camera = new_cameras[index]
                # print(new_camera.ip_address)
                mac_address = discovered_models[model_name][index][0]
                device_ip = discovered_models[model_name][index][1]
                # print(mac_address)
                # self.save_mac_address(new_camera, mac_address)
                # self.setup_device(new_camera, device_ip)
                print("{}\t{}\t{}\t{}".format(
                    new_camera.model.name,
                    new_camera.get_upnp_name(),
                    new_camera.ip_address,
                    new_camera.mac_address
                ))
                index += 1


   
        
        