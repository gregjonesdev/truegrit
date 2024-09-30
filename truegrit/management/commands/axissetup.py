import subprocess
import ipaddress

from django.core.management.base import BaseCommand

subnet = ipaddress.ip_network('10.10.0.0/24')

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

    def handle(self, *args, **options):
        for ip in subnet.hosts():
            if self.ping_ip(ip):
                print(f"{ip} is reachable")
            else:
                print(f"{ip} is not reachable")    
