from flask import Flask, Response, Blueprint, jsonify, render_template, request, redirect, url_for
from requests.auth import HTTPDigestAuth
import requests
import pandas as pd
import cv2
import threading
import time
import json
import subprocess
import ipaddress

# Initialize Flask app and blueprint
app = Flask(__name__, static_url_path='/static')
views = Blueprint("views", __name__)

# Configuration variables
base_url_list = ["http://10.10.10.30", "http://10.10.10.31", "http://10.10.10.32", "http://10.10.10.34", "http://10.10.10.115", "http://10.10.10.111"]
username = "admin"
password = "1234"

# Session for HTTP requests
session = requests.Session()
session.auth = HTTPDigestAuth(username, password)

# Global variables
relay_df = None
feed_data = None
network_df = None

# Locks for thread-safe access to data
relay_df_lock = threading.Lock()
feed_data_lock = threading.Lock()
network_df_lock = threading.Lock()

# Function to update relay information
def get_relay_info(base_url, relay_number):
    """
    Fetch relay information from the given base URL and relay number.
    """
    url = f"{base_url}/restapi/relay/outlets/{relay_number}/"
    headers = {"Accept": "application/json"}
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Error occurred for {base_url} relay {relay_number}: {err}")
    return None

def update_relay_info_background():
    """
    Background thread function to update relay information periodically.
    """
    global relay_df
    while True:
        relay_data = get_all_relay_info(base_url_list)
        with relay_df_lock:
            relay_df = relay_data
        time.sleep(60)

def get_all_relay_info(base_url_list):
    """
    Retrieve relay information for all devices in the base URL list.
    """
    relay_data = []
    for base_url in base_url_list:
        for relay_number in range(8):
            relay_info = get_relay_info(base_url, relay_number)
            relay_data.append({
                "Device IP": base_url,
                "Relay Number": relay_number,
                "Name": relay_info.get("name", "N/A") if relay_info else "N/A",
                "State": relay_info.get("state", "N/A") if relay_info else "N/A"
            })
    return pd.DataFrame(relay_data)

def get_relay_state(base_url, relay_number):
    """
    Fetch the state of a relay from the given base URL and relay number.
    """
    url = f"{base_url}/restapi/relay/outlets/{relay_number}/state/"
    headers = {"Accept": "application/json"}
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
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

def set_relay_state(base_url, relay_number, state):
    """
    Set the state of a relay at the given base URL and relay number.
    """
    url = f"{base_url}/restapi/relay/outlets/{relay_number}/state/"
    headers = {"X-CSRF": "x"}
    data = {"value": "true" if state else "false"}
    try:
        response = session.put(url, headers=headers, data=data)
        response.raise_for_status()
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

# RTSP camera URLs - 720p
rtsp_url1 = "rtsp://10.10.10.1:7447/AO4GXNrvifLWO7lB"
rtsp_url2 = "rtsp://10.10.10.1:7447/baPlAstf3mmfGQTh"

def generate_frames(camera):
    """
    Generate video frames from the given camera URL.
    """
    cap = cv2.VideoCapture(rtsp_url1 if camera == 1 else rtsp_url2)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()

def start_video_feed(camera):
    """
    Start a background thread to generate video frames for the given camera.
    """
    app.logger.info(f"Starting video feed for camera {camera}")
    thread = threading.Thread(target=generate_frames, args=(camera,))
    thread.daemon = True
    thread.start()
    return thread

# Network Monitoring
LIBRENMS_API_URL = "http://10.10.10.226/api/v0"
API_TOKEN = "0bfe448e61f87ac87a0f16db0007c85f"

headers = {
    "X-Auth-Token": API_TOKEN
}

def get_devices():
    try:
        response = requests.get(f"{LIBRENMS_API_URL}/devices", headers=headers)
        response.raise_for_status()
        start_index = response.text.find('{')
        if start_index == -1:
            return []

        json_content = response.text[start_index:]
        devices_data = json.loads(json_content)

        devices = []
        for device in devices_data.get('devices', []):
            device_id = device.get('device_id')
            ip = device.get('ip')
            sysname = device.get('sysName', 'Unknown')
            display_name = device.get('displayName', sysname)  # Check if displayName exists
            device_type = device.get('type', 'Unknown')  # Get the device type

            # Map device type to group
            if device_type == "appliance":
                device_group = "Satcom Systems"
            elif device_type == "wireless":
                device_group = "Routers"
            elif device_type == "network":
                device_group = "Lab Network"
            else:
                device_group = "Other"

            is_pingable, ping_time = ping_device(ip)
            devices.append({
                "device_id": device_id,
                "ip": ip,
                "display_name": display_name,
                "device_group": device_group,
                "ping_status": is_pingable,
                "ping_time": ping_time
            })
        return devices
    except requests.exceptions.RequestException as err:
        print(f"Error in API request: {err}")
        return []

def update_network_info_background():
    """
    Background thread function to update network information periodically.
    """
    global network_df
    while True:
        network_data = get_devices()
        with network_df_lock:
            network_df = pd.DataFrame(network_data)
        time.sleep(60)

def ping_device(ip):
    """
    Ping a device to check its availability.
    """
    try:
        start_time = time.time()
        output = subprocess.run(["ping", "-c", "1", ip], capture_output=True, text=True, timeout=2)
        end_time = time.time()
        is_pingable = output.returncode == 0
        ping_time = (end_time - start_time) * 1000  # Convert to milliseconds
        return is_pingable, ping_time
    except subprocess.TimeoutExpired:
        return False, None

# Start video feed threads
thread_frames1 = start_video_feed(1)
thread_frames2 = start_video_feed(2)

# View definitions
@views.route("/")
def home():
    """
    Home page displaying relay information and video feeds.
    """
    global relay_df
    with relay_df_lock:
        current_relay_df = relay_df.copy()  # Ensure thread-safe access to relay_df
    return render_template("index.html", relay_df=current_relay_df, feed_data=feed_data)

@views.route("/change_relay_state", methods=["POST"])
def change_relay_state():
    """
    Change the state of a relay.
    """
    relay_number = int(request.form.get("relay_number"))
    base_url = request.form.get("base_url")
    current_state = get_relay_state(base_url, relay_number)
    if current_state is not None:
        new_state = not current_state
        set_relay_state(base_url, relay_number, new_state)
        update_relay_info()
    return redirect(url_for("views.power"))

@views.route("/update_relay_info", methods=["GET"])
def update_relay_info():
    """
    Manually update relay information.
    """
    global relay_df
    relay_df = get_all_relay_info(base_url_list)

@views.route("/power")
def power():
    """
    Display the power control page.
    """
    return render_template("power.html", relay_df=relay_df)

@views.route("/feed")
def feed():
    """
    Display the video feed page.
    """
    return render_template("feed.html")

@views.route("/video_feed/<int:camera>")
def video_feed(camera):
    """
    Provide video feed for the given camera.
    """
    return Response(generate_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@views.route("/network")
def network():
    """
    Display the network page.
    """
    global network_df
    group_filter = request.args.get('group')
    
    with network_df_lock:
        current_network_df = network_df.copy()  # Ensure thread-safe access to network_df

    if group_filter:
        current_network_df = current_network_df[current_network_df['device_group'] == group_filter]
    
    devices = current_network_df.to_dict(orient='records')
    return render_template("network.html", devices=devices, filter_group=group_filter)

@views.route('/ping_device/<device_ip>', methods=['POST'])
def ping_device_route(device_ip):
    """
    Route to ping a device and return the status.
    """
    is_pingable, ping_time = ping_device(device_ip)
    return jsonify({"ping_status": is_pingable, "ping_time": ping_time})

@app.route('/calculate_subnet', methods=['POST'])
def calculate_subnet():
    data = request.json
    ip = data.get('ip')
    subnet = int(data.get('subnet'))

    try:
        network = ipaddress.IPv4Network(f"{ip}/{subnet}", strict=False)
        network_address = network.network_address
        broadcast_address = network.broadcast_address
        subnet_mask = str(network.netmask)
        usable_ips = list(network.hosts())
        first_usable_ip = usable_ips[0] if usable_ips else None
        last_usable_ip = usable_ips[-1] if usable_ips else None
        
        result = {
            'ip': ip,
            'subnet': subnet,
            'network_address': str(network_address),
            'broadcast': str(broadcast_address),
            'usable_ip_range': str(first_usable_ip) + " - " + str(last_usable_ip),
            'mask': str(subnet_mask)
        }
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

# Register blueprint
app.register_blueprint(views, url_prefix="")

# Running the app
if __name__ == '__main__':
    relay_update_thread = threading.Thread(target=update_relay_info_background)
    relay_update_thread.daemon = True
    relay_update_thread.start()

    network_update_thread = threading.Thread(target=update_network_info_background)
    network_update_thread.daemon = True
    network_update_thread.start()
    
    app.run(host='0.0.0.0', port=8000)
