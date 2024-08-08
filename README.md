# Lab Web Application

This project is a Flask-based web application designed for managing and monitoring networked devices, including lab equipment and SATCOM systems. The application provides real-time access to device information, control over relay states, live video feeds from RTSP cameras, and network monitoring via LibreNMS.

**Power Controls**: Users can remotely control the state of relays, which are critical for managing various configurations within the networked environment.

**Live Video Feeds**: The application supports live streaming of video from RTSP cameras, providing users with a visual feed of SATCOM antennas.

**Network Monitoring**: Integrated with LibreNMS, the application enables comprehensive network monitoring. It tracks device status, internet connectivity, and SNMP results.

**IP Subnet Calculator**: Users can calculate subnet information based on IP address and subnet mask represented in CIDR notation.

## Project Structure

lab-webpage/
│
├── static/
│ └── (Static files like CSS, JS, images)
│
├── templates/
│ ├── base.html
│ ├── feed.html
│ ├── index.html
│ ├── network.html
│ └── power.html
│
├── app.py
├── README.md
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

## Subnet Calculator Function
* calculate_subnet(): Calculates subnet information based on IP address and subnet mask.

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

* '/calculate_subnet': Calculates subnet information based on IP address and subnet mask.

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
