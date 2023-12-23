#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <MFRC522.h>

const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";
const char* server = "your_cloud_server_address";
const int port = 80; // or the port your server is running on
const int buttonPin = D2; // Replace with the actual pin connected to your button

LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C address 0x27, 16 columns, and 2 rows
MFRC522 rfidReader(D3, D4);  // Replace with the actual RFID reader pins

unsigned long lcdOffTime = 0; // Variable to store the time when LCD was turned off
const unsigned long lcdOffDelay = 5000; // Time in milliseconds before turning off LCD

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");

  lcd.begin(16, 2);  // initialize the lcd
  lcd.backlight();   // turn on the backlight

  pinMode(buttonPin, INPUT_PULLUP);

  SPI.begin();
  rfidReader.PCD_Init();
}

void loop() {
  if (rfidReader.PICC_IsNewCardPresent() && rfidReader.PICC_ReadCardSerial()) {
    // RFID card detected, read the card data
    String rfidCard = "";
    for (byte i = 0; i < rfidReader.uid.size; i++) {
      rfidCard += String(rfidReader.uid.uidByte[i] < 0x10 ? "0" : "");
      rfidCard += String(rfidReader.uid.uidByte[i], HEX);
    }

    rfidReader.PICC_HaltA();
    rfidReader.PCD_StopCrypto1();

    // Determine the action based on button press
    String action = digitalRead(buttonPin) == HIGH ? "enter" : "exit";

    // Use HTTPClient to send POST request
    HTTPClient http;
    http.begin("http://" + String(server) + ":" + port + "/process_data");
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    String dataToSend = "rfid_card=" + rfidCard + "&action=" + action;

    int httpCode = http.POST(dataToSend);

    if (httpCode > 0) {
      String payload = http.getString();
      Serial.println("Response: " + payload);

      if (payload.startsWith("1")) {
        // Access granted
        String username = payload.substring(2);
        lcd.clear();
        lcd.print("Welcome " + username);
        lcd.setCursor(0, 1);
        lcd.print(action == "enter" ? "Have a good day!" : "Safe travels!");
        lcdOffTime = millis() + lcdOffDelay; // Set the time to turn off LCD
      } else {
        // Access denied
        lcd.clear();
        lcd.print("Access denied!");
        lcd.setCursor(0, 1);
        lcd.print("Please go back.");
        lcdOffTime = millis() + lcdOffDelay; // Set the time to turn off LCD
      }
    } else {
      Serial.println("Error on HTTP request");
    }

    http.end();
  }

  // Check if it's time to turn off the LCD
  if (millis() > lcdOffTime && lcdOffTime != 0) {
    lcdOffTime = 0; // Reset the time
    lcd.noBacklight(); // Turn off the backlight
  }

  // Check RFID every 500 milliseconds
  delay(500);
}
