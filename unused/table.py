""" 
import requests
from request import get_all_relay_info
from requests.auth import HTTPDigestAuth
import pandas as pd


def set_relay_state(base_urls, relay_number, state, username, password):
    for base_url in base_urls:
        url = f"{base_url}/restapi/relay/outlets/{relay_number}/state/"
        headers = {
            "X-CSRF": "x",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data = {
            "value": state  # Update the state directly
        }

        try:
            response = requests.put(url, headers=headers, json=data, auth=HTTPDigestAuth(username, password))
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


# Configuration
base_url_list = [
    "http://10.10.10.30",
    "http://10.10.10.31",
    "http://10.10.10.32",
    "http://10.10.10.34",
    "http://10.10.10.115",
    "http://10.10.10.111"
]
username = "admin"
password = "1234"

# Fetch relay data
relay_df = get_all_relay_info(base_url_list, username, password)
print(relay_df)

# Example usage: Set a relay state (for testing purposes)
# relay_number = 0
# state = True  # True for "on", False for "off"
# set_relay_state(base_url_list, relay_number, state, username, password)
"""