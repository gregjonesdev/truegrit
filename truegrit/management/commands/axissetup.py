import subprocess
import ipaddress
import requests
from requests.auth import HTTPBasicAuth
from django.core.management.base import BaseCommand

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
        
    def updateProperty(self. property, value):
        pass
        # send request here    
        
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
        # root.Network.BootProto=dhcp
        # root.Network.Broadcast=192.168.0.255
        # root.Network.DefaultRouter=192.168.0.1
        # root.Network.DNSServer1=0.0.0.0
        # root.Network.DNSServer2=0.0.0.0
        # root.Network.DomainName=
        # root.Network.Enabled=yes
        # root.Network.HostName=axis-b8a44fb6206d
        # root.Network.IPAddress=192.168.0.90
        # root.Network.Media=auto
        # root.Network.SubnetMask=255.255.255.0     
        
    def disableHTTPS(self, ip):
        pass
        # root.HTTPS.Enabled=yes 
        # not quite
        # http://10.10.0.2/axis-cgi/param.cgi?action=update&root.HTTPS.Enabled=no
   
        
    def updateUPnP(self, name, ip):
        pass
        # success, if logged in
        # http://10.10.0.2/axis-cgi/param.cgi?action=update&root.Network.UPnP.FriendlyName=DidThisWork

    def handle(self, *args, **options):
        print(requests.get(url, auth=HTTPBasicAuth(username, password)))
        # for ip in subnet.hosts():
        #     if self.ping_ip(ip):
        #         print(f"{ip} is reachable")
        #     else:
        #         print(f"{ip} is not reachable")    


        # http://10.10.0.2/axis-cgi/param.cgi?action=list
        
        