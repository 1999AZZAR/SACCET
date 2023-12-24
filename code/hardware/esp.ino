// RFID Access Control System by azzar

// Features

// - Read RFID card information.
// - Connect to a Wi-Fi network for data communication.
// - Send RFID card data and action (enter/exit) to a cloud server.
// - Display messages on an LCD screen based on server responses.
// - Illuminate LEDs (green for access granted, red for access denied).

// library
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <MFRC522.h>

// some credentials and other assignmen
const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";
const char* server = "your_cloud_server_address";
const int port = 80;
const int buttonPin = D2;
const int greenLedPin = D5;
const int redLedPin = D6;

LiquidCrystal_I2C lcd(0x27, 16, 2);
MFRC522 rfidReader(D3, D4);

unsigned long lcdOffTime = 0;
const unsigned long lcdOffDelay = 5000;

// granted access handler
void access_granted(String username, String action) {
  digitalWrite(greenLedPin, HIGH);
  lcd.clear();
  lcd.print("Welcome " + username);
  lcd.setCursor(0, 1);
  lcd.print(action == "enter" ? "Have a good day!" : "Safe travels!");
  lcdOffTime = millis() + lcdOffDelay;
}

// denied access handler
void access_denied() {
  digitalWrite(redLedPin, HIGH);
  lcd.clear();
  lcd.print("Access denied!");
  lcd.setCursor(0, 1);
  lcd.print("Please go back.");
  lcdOffTime = millis() + lcdOffDelay;
}

// connection handler
void handle_connection(String rfidCard, String action) {
  WiFiClient client;
  HTTPClient http;

  String url = "http://" + String(server) + ":" + port + "/process_data";
  http.begin(client, url);
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");

  String dataToSend = "rfid_card=" + rfidCard + "&action=" + action;

  int httpCode = http.POST(dataToSend);

  if (httpCode > 0) {
    String payload = http.getString();
    Serial.println("Response: " + payload);

    if (payload.startsWith("1")) {
      access_granted(payload.substring(2), action);
    } else {
      access_denied();
    }
  } else {
    Serial.println("Error on HTTP request");
  }

  http.end();
}

// rfid reading handler
void read_rfid() {
  if (rfidReader.PICC_IsNewCardPresent() && rfidReader.PICC_ReadCardSerial()) {
    String rfidCard = "";
    for (byte i = 0; i < rfidReader.uid.size; i++) {
      rfidCard += String(rfidReader.uid.uidByte[i] < 0x10 ? "0" : "");
      rfidCard += String(rfidReader.uid.uidByte[i], HEX);
    }

    rfidReader.PICC_HaltA();
    rfidReader.PCD_StopCrypto1();

    String action = digitalRead(buttonPin) == HIGH ? "enter" : "exit";

    handle_connection(rfidCard, action);
  }
}

// setup handler
void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");

  lcd.begin(16, 2);
  lcd.backlight();

  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(greenLedPin, OUTPUT);
  pinMode(redLedPin, OUTPUT);

  digitalWrite(greenLedPin, LOW);
  digitalWrite(redLedPin, LOW);

  SPI.begin();
  rfidReader.PCD_Init();
}

// loop handler
void loop() {
  read_rfid();

  if (millis() > lcdOffTime && lcdOffTime != 0) {
    lcdOffTime = 0;
    lcd.noBacklight();
    digitalWrite(greenLedPin, LOW);
    digitalWrite(redLedPin, LOW);
  }

  delay(500);
}
