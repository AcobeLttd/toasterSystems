/* Eventually the entire code here is going to get a rewrite :3 i dont really like how it looks as of now. I would like to make it easier to interact with the serial reading/sending in the future. 
What i want to implement in the future:
  Better command management system, similar to how im handing it in on the pi. 
  Integration for i2c and webserver in the future.
  And thats basically it.
  Also would want to improve the ping code cuz like holy sheet is it ass, maybe ill split it up into multiple files similarlly in how im doing it in python otherwise its going to get very big and unmanageble quickly.
*/

#include <Arduino.h>

// Imports wifi library thing and fs.
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "LittleFS.h"
#include <ArduinoJson.h>
#include <ESPmDNS.h>
#include <WiFi.h>

const uint8_t SerialTXPin = 43;
const uint8_t SerialRXPin = 44;

// Network credentials for the ESP32 AP.
const char *ssid = "ESP32-S3-Progen";
const char *password = "IamBigStrongPassword2";

// Setup mdns
const char* mdnsName = "progen";

// Setup WiFi thingi
const char IPConfigMessage[] = R"rawr(Screen on IP:
%d.%d.%d.%d
SSID:
%s
Password:
%s
mDNS:%s)rawr";


// Timings

struct{
  unsigned long currentTimeMicr;
  unsigned long pastTime;
  unsigned long startPing;
  unsigned long pingTime;

} tMicro = { 0, 0, 0, 0 };

struct{
  unsigned long currentTimeMillis;
  unsigned long keepPinging;
  unsigned long lastResponse;
  unsigned long pastTime;
} tMillis = { 0, 0, 0, 0 };

// Delay times millis
uint32_t jsonSendDelay = 100;

// Ping related

unsigned long totalPing = 0;
uint8_t counter;

// Ping bools
bool pingToggle = false;
bool pingRec = false;
bool timeoutPing = false;

// Raspi connection Bools

bool connection = true;
bool piOff = false;



// Webserver related
// Create AsyncWebServer object on port 80
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

// Makes a global JSON document.
JsonDocument globalJson;
void initJSON() {
  globalJson["piConnect"] = false;
  globalJson["lastMessage"] = 0;
}



// Initializes websocket

void initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}

// Webserver functions

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo *)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, data, len);
    if (error) {
      return;
    }
    
    const char *command = doc["command"] | "";

    debugSend(String((char *)command));

    Serial2.println((char *)command);
    
  }
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  char buffer[128];
  switch (type) {
    case WS_EVT_CONNECT:
      
      snprintf(buffer, sizeof(buffer),"\nWebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      debugSend(String(buffer));
      break;
    case WS_EVT_DISCONNECT:
      snprintf(buffer, sizeof(buffer),"\nWebSocket client #%u disconnected\n", client->id());
      debugSend(String(buffer));
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

// LittleFS mounting
void initLittleFS() {
  if (!LittleFS.begin()) {
    debugSend("Error, littlefs didnt mount properly.");
    Serial2.println("Error, littlefs didnt mount properly.");
    return;
  }
  File file = LittleFS.open("/index.html", "r");
  if (!file) {
    debugSend("Failed to open file.");
    Serial2.println("Failed to open file.");
    return;
  }

  file.close();
}

// mDNS
// initMDNS
void initMDNS() {
  if (!MDNS.begin(mdnsName)){
    debugSend("mDNS Error");

    while(1) {
      delay(1000);
    }
  }
  MDNS.addService("_http", "_tcp", 80);
  debugSend("mDNS started.");
}


// Sends JSON
void send() {
  if (tMillis.currentTimeMillis - tMillis.pastTime >= jsonSendDelay) {
    const size_t len = measureJson(globalJson);

    // original API from me-no-dev
    AsyncWebSocketMessageBuffer *buffer = ws.makeBuffer(len);
    assert(buffer);  // up to you to keep or remove this
    serializeJson(globalJson, buffer->get(), len);
    ws.textAll(buffer);
    tMillis.currentTimeMillis = tMillis.pastTime;
  }
  
}

// Serial functions

String readSerial2() {
  String msg = Serial2.readStringUntil('\n');
  msg.trim();
  return msg;
}

String readSerial() {
  String msg = Serial.readStringUntil('\n');
  msg.trim();
  return msg;
}

void debugSend(String debugMessage) {
  char buffer[128];
  unsigned long seconds = millis() / 1000;

  unsigned long hours = seconds / 3600;
  unsigned long minutes = (seconds % 3600) / 60;
  unsigned long secs = seconds % 60;
  snprintf(buffer, sizeof(buffer),"[%02lu:%02lu:%02lu] %s", hours, minutes, secs, debugMessage.c_str());
  // Serial.println(buffer);
  globalJson["debug"] = buffer;
}

// Ping functions

void pingIng() {
  tMicro.startPing = micros();
  Serial2.println("ping");
}

void pingDetect(String sah) {
  if (sah == "ping 100") {
    pingToggle = !pingToggle;
    pingIng();
    counter = 0;
    tMicro.pastTime = tMicro.currentTimeMicr;
  } else if (sah == "ping") {
    tMicro.startPing = micros();
    tMicro.pastTime = tMicro.currentTimeMicr;
  }
}

void detectPong(String readse) {
  if (readse == "pong") {
    tMicro.pingTime = micros() - tMicro.startPing;
    totalPing = totalPing + tMicro.pingTime;
    char buffer[128];
    snprintf(buffer, sizeof(buffer),"ping time %lu microsec \n", tMicro.pingTime);
    debugSend(String(buffer));
    pingRec = true;
  }
}

void multiplePing() {
  if (counter == 100) {
    pingToggle = false;
    debugSend(String(totalPing));
    char buffer[128];
    snprintf(buffer, sizeof(buffer),"Average ping in microseconds after 100 pings = %.4f \n", totalPing / 100.0000);
    debugSend(String(buffer));
    totalPing = 0;
    counter = 0;
  }

  else if (pingToggle && pingRec && (micros() - tMicro.pastTime >= 100000)) {
    char buffer[128];
    snprintf(buffer, sizeof(buffer),"Sent ping %lu \n", counter);
    debugSend(String(buffer));
    pingIng();
    tMicro.pastTime = tMicro.currentTimeMicr;
    pingRec = false;
    counter++;
  }
}

// Pi related code

void isPiThere() {
  if (!piOff) {
    if ((tMillis.currentTimeMillis - tMillis.lastResponse >= 40000) && !timeoutPing) {
      debugSend("No response in 40000 sending ping.");
      pingIng();
      debugSend("ping sent.");
      timeoutPing = true;
    } else if ((tMillis.currentTimeMillis - tMillis.lastResponse >= 45000) && connection) {
      debugSend("No connection from pi.");
      pingIng();
      connection = false;
    }
    if ((!connection) && tMillis.currentTimeMillis - tMillis.keepPinging >= 1000) {
      pingIng();
      debugSend("Sent ping. Retry every second.");
      tMillis.keepPinging = tMillis.currentTimeMillis;
    }
  }
}


// WiFi related code
void displayIP() {
  char buf[128];  // Creates a 128 byte temporary buffer where it later loads in the string to be printed out.
  IPAddress WiFiIP = WiFi.softAPIP();
  sprintf(buf, IPConfigMessage, WiFiIP[0], WiFiIP[1], WiFiIP[2], WiFiIP[3], ssid, password, mdnsName);  // Loads the dynamic variables such as IP address, SSID and Password into the buffer and converts them into a string using the IPConfigMessage template.
  debugSend(String(buf));
}

void setup() {
  //Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, SerialRXPin, SerialTXPin);

  
    // Starts the WiFI AP
  WiFi.softAP(ssid, password);

  initJSON();
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

  debugSend("Esp32 online");
  Serial2.println("Esp32 online");

  tMillis.lastResponse = millis();
}

void loop() {
  tMicro.currentTimeMicr = micros();
  tMillis.currentTimeMillis = millis();

  if (Serial2.available() > 0) {
    char buffer[128];
    snprintf(buffer, sizeof(buffer),"Last Response from pi %lu millis ago. \n", tMillis.currentTimeMillis - tMillis.lastResponse);
    debugSend(String(buffer));
    tMillis.lastResponse = tMillis.currentTimeMillis;
    connection = true;
    String readse = readSerial2();
    snprintf(buffer, sizeof(buffer),"From Pi: %s\n", readse.c_str());
    debugSend(String(buffer));

    detectPong(readse);
    if (readse == "Shutting down") {  //this stops the code from repeating the pinging forever. You would need to power off to reset this.
      piOff = true;
    }
  }

  if (Serial.available() > 0) {
    String sah = readSerial();
    Serial2.println(sah);
    debugSend(sah);
    pingDetect(sah);
  }
  
  isPiThere();
  multiplePing();
  send();
}
