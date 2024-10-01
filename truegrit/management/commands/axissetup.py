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
        print("Update camera {}: {} to {}".format(ip_address, property, value))
        url = "http://{}/axis-cgi/param.cgi?action=update&{}={}".format(
            ip_address,
            property,
            value
        )
        response = requests.get(url, auth=HTTPDigestAuth(username, password))
        if not response.status_code == 200:
            print("Something went wrong...")
            print(response.__dict__)
            raise SystemExit(0)
        else:
            print("Success!")

   
        
    def updateAuthMethod(self):
        pass
        # Turn off 802.1 authentication:
        # root.Network.Interface.I0.dot1x.Enabled yes -> no
        # root.Network.Interface.I0.dot1x.Status Unauthorized -> Stopped    
        
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

        
        
    def disableHTTPS(self, ip):
        pass
        # root.HTTPS.Enabled yes -> no
        # not quite
        # http://10.10.0.2/axis-cgi/param.cgi?action=update&root.HTTPS.Enabled=no
   
        
    def updateUPnP(self, name, ip):
        pass
        # success, if logged in
        # http://10.10.0.2/axis-cgi/param.cgi?action=update&root.Network.UPnP.FriendlyName=DidThisWork

    def handle(self, *args, **options):
        ip_address = "10.19.54.108"
        camera = Camera.objects.get(ip_address=ip_address)
        print(camera.get_upnp_name())
        raise SystemExit(0)
        property = "root.Network.UPnP.FriendlyName"
        value = "00195-Dept Produce 03"
        self.updateProperty(ip_address, property, value)
        # print(subprocess)
        # url = "http://{}/axis-cgi/device/attributes.cgi".format("10.19.54.108")
        # print(requests.get(url, auth=HTTPBasicAuth(username, password)))
        # for ip in subnet.hosts():
        #     if self.ping_ip(ip):
        #         print(f"{ip} is reachable")
        #     else:
        #         print(f"{ip} is not reachable")    


        # http://10.10.0.2/axis-cgi/param.cgi?action=list
        
        