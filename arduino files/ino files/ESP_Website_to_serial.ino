/*********
  Rui Santos & Sara Santos - Random Nerd Tutorials
  Complete project details at https://RandomNerdTutorials.com/esp32-websocket-server-arduino/
  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*********/

// Import required libraries
#include <Arduino.h>

// AdaFruit OLED Libaries
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
// Load Wire library for I2C serial commuications.
#include <Wire.h>

// Load Wifi and ESPAsyncWebServer libraries for the webserver and websockets
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "LittleFS.h"
#include <ArduinoJson.h>
#include <ESPmDNS.h>

//Oled defines
#define screenWidth 128
#define screenHeight 64

#define oledAdress 0x3C

#define oledReset -1

Adafruit_SSD1306 display(screenWidth, screenHeight, &Wire, oledReset);

// Serial2 coms setup
const uint8_t SerialTXPin = 43;
const uint8_t SerialRXPin = 44;

// Network credentials for the ESP32 AP.
const char *ssid = "ESP32-S3-Relay";
const char *password = "IamBigStrongPassword2";

// Setup mdns
const char* mdnsName = "progen";


// Defines the pins for the diffrent components connected to the ESP32-S3



// Millis for non-blocking delays.

struct {
  unsigned long currentTime;
  unsigned long pastMain;
  unsigned long pastPir;
  unsigned long pastPirDelay;
  unsigned long pastSerialMessage;
  unsigned long pastOverride;
} t = { 0, 0, 0, 0, 0 };

uint32_t displayDelay = 100;            // 100 millisec delay
uint32_t pirRefreshDelay = 1000;        // 1 sec delay
uint32_t serialMessageInterval = 1000;  // 2 Sec intervals.
uint32_t startDelayTime = 10000;        // 5 Secs start delay if enabled.
uint32_t overrideDelay = 5 * 60000;     // 5 mins delay to disable the override.

uint32_t pirDelay = 0;  // Used as a variable to update how long it takes for the light to turn off automatically after the PIR has stopped detecting.

bool relayState = false;

//The delays determine how often the display and pirSensor status is refreshed.


// Makes a global json variable which can be read any time.
char globalJson[256];




// Create AsyncWebServer object on port 80
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

const char IPConfigMessage[] = R"rawr(Screen on IP:
%d.%d.%d.%d
SSID:
%s
Password
%s)rawr";


const char SerialMessage[] = R"rawr(
Display updated and pot read with value %u and pir delay is at %u Milliseconds or %u mins
Time since last activation: %u secs.)rawr";



// Websocket setup code underneath.

// This is the handler for event information. It detects when the client has pressed the button.

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo *)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, data, len);
    if (error) {
      return;
    }
    
    const char *command = doc["command"] | "";

    if (strcmp((char *)command, "toggle") == 0) {
      relayState = !relayState;
      t.pastPirDelay = t.currentTime;
    }
  }
}

// Webhook code which serial prints when clients. I dont have a full understanding of this as this is from the original code.

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("\nWebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("\nWebSocket client #%u disconnected\n", client->id());
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

// Initialises the websocket

void initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}

// Littlefs loading
void initLittleFS() {
  if (!LittleFS.begin()) {
    Serial.println("Error, littlefs didnt mount properly.");
    Serial2.println("Error, littlefs didnt mount properly.");
    return;
  }
  File file = LittleFS.open("/index.html", "r");
  if (!file) {
    Serial.println("Failed to open file.");
    Serial2.println("Failed to open file.");
    return;
  }

  file.close();
}

// initMDNS
void initMDNS() {
  if (!MDNS.begin(mdnsName)){
    Serial.println("mDNS Error");
    while(1) {
      delay(1000);
    }
  }
  MDNS.addService("_http", "_tcp", 80);
  Serial.println("mDNS started.");
}


// Initialises Json

void sendStat(bool state1, bool state2, bool state3, uint16_t state4, long state5) {
  JsonDocument doc;
  doc["state"] = state1;
  doc["pirState"] = state2;
  doc["pirOverride"] = state3;
  doc["delay"] = state4;
  doc["pirTime"] = state5;
  serializeJson(doc, globalJson, sizeof(globalJson));
  send(doc);
}

// Sends the json information to the server. This code snippit taken from offical ESP32AsyncWebServer example code.

void send(JsonDocument &doc) {
  const size_t len = measureJson(doc);

  // original API from me-no-dev
  AsyncWebSocketMessageBuffer *buffer = ws.makeBuffer(len);
  assert(buffer);  // up to you to keep or remove this
  serializeJson(doc, buffer->get(), len);
  ws.textAll(buffer);
}

// Non websocket code.

// Function to send information to serial monitor.

void serialUpdate() {
  char buf[256];
  sprintf(buf, SerialMessage, 453345345 / 60000, 232, 435345435 / 60000, (t.currentTime - t.pastPirDelay) / 1000);
  Serial.println(buf);
  Serial.println("\nNotified clients with new json:");
  Serial.println(globalJson);
}


// Function to display the IP address, SSID and WiFi password on the OLED display.


void displayIP() {
  char buf[128];  // Creates a 128 byte temporary buffer where it later loads in the string to be printed out via the display and serial monitor.
  IPAddress WiFiIP = WiFi.softAPIP();
  sprintf(buf, IPConfigMessage, WiFiIP[0], WiFiIP[1], WiFiIP[2], WiFiIP[3], ssid, password);  // Loads the dynamic variables such as IP address, SSID and Password into the buffer and converts them into a string using the IPConfigMessage template.
  Serial.println("\nDisplayIP called. Displaying IP and AP information on screen as well as serial monitor.");
  Serial.println(buf);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println(buf);
  display.display();
}

// Function used to display the state of the relay.

void displayState(bool x, bool pirS, uint8_t potentiometer) {

  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(10, 2);
  display.println("Relay 1 Pir Status");
  display.setCursor(8, 20);
  display.print("Relay Shutoff Delay");
  display.setCursor(5, 35);
  display.setTextSize(3);
  display.print(potentiometer);
  display.setCursor(70, 35);
  display.print("min");

  // The code under here is for all the squares and things for the display. Basically just layout and making it pretty.
  display.drawRect(0, 14, screenWidth, screenHeight - 14, WHITE);
  display.drawRect(0, 0, screenWidth - 75, 14, WHITE);
  display.drawRect(screenWidth - 75, 0, 75, 14, WHITE);

  // Code under here is to dynamically change a circle to be filled or not filled depending on the state of the relay or pir sensor. Basically also just to make the thing prettier while still displaying useful information.

  if (x) {
    display.fillCircle(5, 5, 3, WHITE);
  } else {
    display.drawCircle(5, 5, 3, WHITE);
  }
  if (pirS) {
    display.fillCircle(screenWidth - 6, 5, 3, WHITE);
  } else {
    display.drawCircle(screenWidth - 6, 5, 3, WHITE);
  }
}
void setup() {
 
  // Serial port for debugging purposes
  // Serial.begin(115200);
  // Starts serial comms for the raspi.
  // Serial2.begin(115200, SERIAL_8N1, SerialRXPin, SerialTXPin);

  // Initialises the OLED display on the I2C bus. (Code from adafruit)

  if (!display.begin(SSD1306_SWITCHCAPVCC, oledAdress)) {

    Serial.println(F("SSD1306 allocation failed"));

    for (;;)
      ;  // Don't proceed, loop forever
  }




  // Starts the WiFI AP
  WiFi.softAP(ssid, password);


  initLittleFS();
  initWebSocket();
  initMDNS();
  

  // Route for root / web page
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(LittleFS, "/index.html", "text/html");
  });
  server.serveStatic("/", LittleFS, "/");

  // Start server
  server.begin();
  // Displays IP information
  displayIP();

  
  




  delay(10000);



  // Fixes the timings as a result of the delay.
  t.pastMain = millis();
  t.pastPir = millis();
  t.pastPirDelay = millis();
  t.pastSerialMessage = millis();
  t.pastOverride = millis();
}

void loop() {
  t.currentTime = millis();                                                     // Sets the currenTime variable in the t structure to the current millis time.

  if (t.currentTime - t.pastMain >= displayDelay) {  // Non-blocking delay to refresh the display and send info to the client website.

    displayState(relayState, 4, 56);                                                    // Updates the display with the newest values.
    sendStat(relayState, 4, 1, 56, (t.currentTime - t.pastPirDelay) / 1000);  // Sends updated values to be processed and sent as a json file to the clients.

    t.pastMain = t.currentTime;  // Updates the past time for the non-blocking delay.
  }


  if (t.currentTime - t.pastSerialMessage >= serialMessageInterval) {  // The serial message intervals.
    serialUpdate();                                                   // calls the SerialUpdate function to update variables in serial monitor for debugging.
  } else if (t.currentTime - t.pastSerialMessage >= serialMessageInterval) {  // Prints an error message to serial every 2 seconds if requireWebserver is true.
    char buf[128];
    sprintf(buf, "\n\n\nNo websocket connected, code innactive. Sent at %ld millis.", t.currentTime);
    Serial.print(buf);
    displayIP();  // Calls the display IP function to print the IP and WiFi AP info in terminal as well as on the OLED.
    display.display();    // Displays the newest information
  }


  if (t.currentTime - t.pastSerialMessage >= serialMessageInterval) t.pastSerialMessage = t.currentTime;  // Updates the past serial message.

  
  ws.cleanupClients();  // Cleans up the webhooks, otherwise memory usage builds up and things start to break. (Part of original code.)
}