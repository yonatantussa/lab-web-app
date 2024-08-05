"""
import requests
from requests.auth import HTTPDigestAuth
import pandas as pd

def get_relay_info(base_url, relay_number, username, password):
    url = f"{base_url}/restapi/relay/outlets/{relay_number}/"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, auth=HTTPDigestAuth(username, password))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Error occurred for {base_url} relay {relay_number}: {err}")
    return None

def get_all_relay_info(base_url_list, username, password):
    relay_data = []
    for base_url in base_url_list:
        for relay_number in range(8):
            relay_info = get_relay_info(base_url, relay_number, username, password)
            relay_data.append({
                "Device IP": base_url,
                "Relay Number": relay_number,
                "Name": relay_info.get("name", "N/A") if relay_info else "N/A",
                "State": relay_info.get("state", "N/A") if relay_info else "N/A"
            })
    relay_df = pd.DataFrame(relay_data)
    return relay_df

def get_relay_state(base_url, relay_number, username, password):
    url = f"{base_url}/restapi/relay/outlets/{relay_number}/state/"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, auth=HTTPDigestAuth(username, password))
        response.raise_for_status()
        
        # Handle the JSON response, which can either be a dict or a direct boolean
        try:
            json_response = response.json()
            if isinstance(json_response, dict):
                return json_response.get("value") == "true"
            elif isinstance(json_response, bool):
                return json_response
            else:
                print(f"Unexpected response type: {type(json_response)}")
                return None
        except ValueError:
            print("Response is not valid JSON")
            return None
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
"""