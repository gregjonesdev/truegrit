import requests
import msal
import json

# Replace these values with your company's information
tenant_id = '....cd6c'  # Azure AD Tenant ID
client_id = '....b573'  # Dynamics 365 Client ID (Application ID)
client_secret = 'your-client-secret'  # Azure AD Client Secret
resource = 'https://pref-techprod.operations.dynamics.com/'  # Base URL of your Dynamics 365 instance
username = 'gregoryjones@pref-tech.com'  # Your username
password = ''  # Your password

# Step 1: Obtain Access Token from Azure AD
def get_access_token():
    authority = f'https://login.microsoftonline.com/{tenant_id}'
    app = msal.PublicClientApplication(client_id, authority=authority)

    # Acquiring token using username and password (resource owner password credentials grant)
    result = app.acquire_token_by_username_password(
        username=username,
        password=password,
        scopes=[f'{resource}/.default']
    )

    if 'access_token' in result:
        return result['access_token']
    else:
        print(f"Error: {result.get('error_description')}")
        return None

# Step 2: Retrieve Timesheet Data from Dynamics 365
def get_timesheets(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Example endpoint to fetch timesheet data
    # Replace this with the actual endpoint of your Dynamics 365 instance for timesheets
    url = f'{resource}/api/data/v9.0/timesheets'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

# Main execution
if __name__ == '__main__':
    access_token = get_access_token()

    if access_token:
        timesheet_data = get_timesheets(access_token)

        if timesheet_data:
            print(json.dumps(timesheet_data, indent=4))  # Pretty-print the data
        else:
            print("No timesheet data found.")
