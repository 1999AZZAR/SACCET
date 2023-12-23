# RFID Access Control System

This simple RFID Access Control System, built for the ESP8266, combines RFID card detection with server communication for basic access management. The system uses an MFRC522 RFID reader and a 16x2 I2C Liquid Crystal Display. The ESP8266 connects to a Wi-Fi network, reads RFID cards, and communicates with a server to determine access status.

## Setup

1. Replace placeholder values in the code (`your_wifi_ssid`, `your_wifi_password`, `your_cloud_server_address`) with your Wi-Fi and server details.
2. Adjust pin configurations (`buttonPin`, `lcd`, and `rfidReader`) based on your hardware setup.

## Functionality

- Detects RFID cards and reads card data.
- Determines access action (enter/exit) based on button press.
- Sends RFID card data and action to a server using HTTP POST.
- Displays user messages on an LCD based on server responses.
- Supports automatic LCD backlight turn-off after a specified delay.

## Usage

1. Upload the code to your ESP8266 device.
2. Ensure the server specified is accessible.
3. Connect the hardware components according to pin configurations.
4. RFID cards trigger access actions, and LCD displays responses.

## Notes

- Ensure proper Wi-Fi connectivity for server communication.
- Monitor the serial monitor for debugging information.
- Customize LCD messages, server details, and actions as needed.
- Further enhancements and integrations can be explored based on project requirements.

Feel free to adapt and extend this simple access control system for your specific needs.
