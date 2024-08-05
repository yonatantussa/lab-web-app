""" import requests
from requests.auth import HTTPDigestAuth

def get_relay_state(base_url, relay_number, username, password):
    url = f"{base_url}/restapi/relay/outlets/{relay_number}/state/"
    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, auth=HTTPDigestAuth(username, password))
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        try:
            return response.json()
        except ValueError:
            return response.text
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
    return None

def set_relay_state(base_url, relay_number, state, username, password):
    url = f"{base_url}/restapi/relay/outlets/{relay_number}/state/"
    headers = {
        "X-CSRF": "x"  # CSRF protection header
    }
    data = {
        "value": "true" if state else "false"  # Form data
    }

    try:
        response = requests.put(url, headers=headers, data=data, auth=HTTPDigestAuth(username, password))
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        try:
            return response.json()
        except ValueError:
            return response.text
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        if response is not None:
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Content: {response.content}")
    return None

base_url = "http://10.10.10.30"
relay_number = 6
username = "admin"
password = "1234"

# Get relay state
relay_state = get_relay_state(base_url, relay_number, username, password)
if relay_state is not None:
    print(f"Relay {relay_number} state: {relay_state}")
else:
    print("Could not retrieve relay state.")

# Set relay state to True (on)
new_state = True
set_response = set_relay_state(base_url, relay_number, new_state, username, password)
if set_response is not None:
    print(f"Relay {relay_number} state set to: {new_state}")
else:
    print("Could not set relay state.")
"""