import subprocess
import ipaddress
import requests
from requests.auth import HTTPDigestAuth
from django.core.management.base import BaseCommand
from truegrit.models import Camera, Network, CameraModel
camera_ip = '10.10.0.2'
username = 'root'
password = 'h3bc4m3r4'
subnet = ipaddress.ip_network('10.10.0.0/24')
new_subnet = ipaddress.ip_network('10.19.54.0/24')

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
        
    def updateIP(self):
        pass
        # root.Network.BootProto: none
        # root.Network.DefaultRouter: 10.20.54.1
        # root.Network.IPAddress: 10.20.54.53
        # root.Network.eth0.Broadcast: 192.168.0.255
        # root.Network.eth0.IPAddress: 10.20.54.53
        # root.Network.eth0.SubnetMask: 255.255.255.0
        # root.Network.Resolver.ObtainFromDHCP: no
        # root.Network.Routing.DefaultRouter: 10.20.54.1
        # root.Network.VolatileHostName.ObtainFromDHCP: no
    
    def updateAuthMethod(self, ip_address):
         # Turn off 802.1 authentication:
        self.updateProperty(ip_address, "root.Network.Interface.I0.dot1x.Enabled", "no")

        # Not working. Unnecessary?
        # self.updateProperty(ip_address, "root.Network.Interface.I0.dot1x.Status", "Stopped")

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
                    discovered_models[model_number].append(mac_address)    
        return discovered_models            


    def scan_cameras(self, camera_count):
        cameras_found = []

        for ip_address in subnet.hosts():
            if self.is_online_camera(ip_address):
                cameras_found.append(ip_address)
                if len(cameras_found) == camera_count:
                    return cameras_found
                # print(f"{ip} is reachable")
            # else:
            #     print(f"{ip} is not reachable") 
            # 
    def is_online_camera(self, ip_address):
        # return self.is_not_gateway(ip_address) and self.ping_ip(ip_address)    
        return self.is_not_gateway(ip_address)

    def setupCamera(self, camera):
        ip_address = camera.ip_address
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
        gateway = "10.10.0.1"
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
        #         self.setupCamera(camera.ip_address)

        # host_numbers = [
        #     14, 153, 157, 159, 162, 168
        # ]
        # for host_number in host_numbers:
        #     ip_address = self.generate_ip_address(gateway, host_number)
        #     camera = Camera.objects.get(ip_address=ip_address)
        #     self.setupCamera(camera)
        # camera_count = 1
        # cameras_found = self.scan_cameras(camera_count)
        # print(cameras_found)
        

        network_list = [
            {
                "number": "10.10.0.1",
                "camera_host_numbers": (38, 45)
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

            for new_camera in new_cameras:
                print(new_camera.ip_address)



        # print(subprocess)
        # url = "http://{}/axis-cgi/device/attributes.cgi".format("10.19.54.108")
        # print(requests.get(url, auth=HTTPBasicAuth(username, password)))
        # for ip in subnet.hosts():
        #     if self.ping_ip(ip):
        #         print(f"{ip} is reachable")
        #     else:
        #         print(f"{ip} is not reachable")    


   
        
        