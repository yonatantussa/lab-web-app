# Lab Web Application

This repository contains the code for a Flask-based web application that interfaces with relays for lab power controls and provides live video feeds of antennas.

## Project Structure

lab-webpage/
│
├── static/
│ └── (Static files like CSS, JS, images)
│
├── templates/
│ ├── index.html
│ ├── power.html
│ ├── feed.html
│ └── network.html
│
├── app.py
└── requirements.txt

## Relay Functions
* get_relay_info: Fetches relay information from the given base URL and relay number.

* update_relay_info_background: Updates relay information periodically in the background.

* get_all_relay_info: Retrieves relay information for all devices in the base URL list.

* get_relay_state: Fetches the state of a relay from the given base URL and relay number.

* set_relay_state: Sets the state of a relay at the given base URL and relay number.

## Video Feed Functions
* generate_frames: Generates video frames from the given camera URL.
* start_video_feed: Starts a background thread to generate video frames for the given camera.

## Network Monitoring Functions
* get_devices(): Fetches network device information from LibreNMS API.
* update_network_info_background(): Updates network information periodically in the background.
* ping_device(ip): Pings a device to check its availability.

## Background Threads
* thread_frames1: Thread for the first video feed.
* thread_frames2: Thread for the second video feed.
* relay_update_thread: Thread for updating relay information periodically.
* network_update_thread: Thread for updating network information periodically.

## Flask Routes
* '/': Home page displaying relay information and video feeds.

* '/change_relay_state': Changes the state of a relay.

* '/update_relay_info': Manually updates relay information.

* '/power': Displays the power control page.

* '/feed': Displays the video feed page.

* '/video_feed': Provides video feed for the given camera.

* '/network': Displays the network page.

* '/ping_device/<device_ip>': Pings a device and returns the status.

## Running the App
```python
if __name__ == '__main__':
    relay_update_thread = threading.Thread(target=update_relay_info_background)
    relay_update_thread.daemon = True
    relay_update_thread.start()

    network_update_thread = threading.Thread(target=update_network_info_background)
    network_update_thread.daemon = True
    network_update_thread.start()
    
    app.run(host='0.0.0.0', port=8000)

## Dependencies
The required dependencies for this project are listed in the requirements.txt file. Install them using:

pip install -r requirements.txt

## Usage
1. Start the Flask application:

python app.py

2. Access the web interface by navigating to 'http://<your_server_ip>:8000' in your web browser.

## Making Changes
To make changes, connect to the server with an FTP client such as FileZilla and transfer the updated files to the application directory. Then, perform the following commands in the server shell:

sudo systemctl daemon-reload

sudo systemctl restart labwebapp.service

To check the status, use the following command:

sudo systemctl status labwebapp.service
