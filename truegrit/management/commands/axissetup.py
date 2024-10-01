import subprocess
import ipaddress
import requests
from requests.auth import HTTPDigestAuth
from django.core.management.base import BaseCommand
from truegrit.models import Camera
camera_ip = '10.10.0.2'
username = 'root'
password = 'h3bc4m3r4'
subnet = ipaddress.ip_network('10.10.0.0/24')
url = f'http://{camera_ip}/axis-cgi/device/attributes.cgi'

GREEN = '\033[92m'
RESET = '\033[0m'

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

    def listSingleValue(self):
        pass
        # works
        # http://10.10.0.2/axis-cgi/param.cgi?action=list&group=root.Brand.ProdFullName    
        
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

        # Not working. Unneccessary?
        # self.updateProperty(ip_address, "root.Network.Interface.I0.dot1x.Status", "Stopped")
    
        
    def disableHTTPS(self, ip_address):
        self.updateProperty(ip_address, "root.HTTPS.Enable", "no")
        self.updateProperty(ip_address, "root.System.BoaGroupPolicy.admin", "http")
        
    def updateUPnP(self, ip_address, upnp_name):
        self.updateProperty(ip_address, "root.Network.UPnP.FriendlyName", upnp_name)
        
    def handle(self, *args, **options):
        ip_address = "10.19.54.107"
        camera = Camera.objects.get(ip_address=ip_address)
        print("Update camera: {}".format(camera.ip_address))
        self.disableHTTPS(ip_address)
        self.updateUPnP(camera.ip_address, camera.get_upnp_name())
        self.updateAuthMethod(ip_address)
        print("Completed successfully")
        # print(subprocess)
        # url = "http://{}/axis-cgi/device/attributes.cgi".format("10.19.54.108")
        # print(requests.get(url, auth=HTTPBasicAuth(username, password)))
        # for ip in subnet.hosts():
        #     if self.ping_ip(ip):
        #         print(f"{ip} is reachable")
        #     else:
        #         print(f"{ip} is not reachable")    


        # http://10.10.0.2/axis-cgi/param.cgi?action=list
        
        