import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

# Define the URL of the login page
url = 'http://example.com/login'

# Your username and password
username = 'admin'
password = ''

def print_info():
    ips = [
        "10.10.0.240",
        "10.10.0.241"
    ]

   # https://10.10.0.240/Softwire/Fable/#/SystemStatus

    for ip in ips:
        url = "http://{}/Softwire/System/Status".format(ip)

        # Send a GET or POST request with Basic Authentication
        response = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Now you can extract specific elements from the parsed HTML
            print(soup)
            # Example 1: Extract the title of the page
            title = soup.title
            print(f"Title of the page: {title.string}")

            # Example 2: Extract all the links (anchor tags) from the page
            links = soup.find_all('a')
            for link in links:
                print(f"Link: {link.get('href')}")