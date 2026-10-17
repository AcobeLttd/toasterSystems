#include <Arduino.h>
const uint8_t SerialTXPin = 43;
const uint8_t SerialRXPin = 44;

unsigned long currentTimeMicr;
unsigned long pastTime;
unsigned long startPing;
unsigned long pingTime;

unsigned long currentTimeMillis;
unsigned long keepPinging;

unsigned long lastResponse;

unsigned long totalPing = 0;

uint8_t counter;

bool pingToggle = false;
bool pingRec = false;
bool timeoutPing = false;
bool connection = true;

bool piOff = false;


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

void pingIng() {
  startPing = micros();
  Serial2.println("ping");
}

void isPiThere() {
  if (!piOff) {
    if ((currentTimeMillis - lastResponse >= 40000) && !timeoutPing) {
      Serial.println("No response in 40000 sending ping.");
      pingIng();
      Serial.println("ping sent.");
      timeoutPing = true;
    } else if ((currentTimeMillis - lastResponse >= 45000) && connection) {
      Serial.println("No connection from pi.");
      pingIng();
      connection = false;
    }
    if ((!connection) && currentTimeMillis - keepPinging >= 1000) {
      pingIng();
      Serial.println("Sent ping. Retry every second.");
      keepPinging = currentTimeMillis;
    }
  }
}

void pingDetect(String sah) {
  if (sah == "ping 100") {
    pingToggle = !pingToggle;
    pingIng();
    counter = 0;
    pastTime = currentTimeMicr;
  } else if (sah == "ping") {
    startPing = micros();
    pastTime = currentTimeMicr;
  }
}

void detectPong(String readse) {
  if (readse == "pong") {
    pingTime = micros() - startPing;
    totalPing = totalPing + pingTime;
    Serial.printf("ping time %lu microsec \n", pingTime);
    pingRec = true;
  }
}

void multiplePing() {
  if (counter == 100) {
    pingToggle = false;
    Serial.println(String(totalPing));
    Serial.printf("Average ping in microseconds after 100 pings = %.4f \n", totalPing / 100.0000);
    totalPing = 0;
    counter = 0;
  }

  else if (pingToggle && pingRec && (micros() - pastTime >= 100000)) {
    Serial.printf("Sent ping %lu \n", counter);
    pingIng();
    pastTime = currentTimeMicr;
    pingRec = false;
    counter++;
  }
}


void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, SerialRXPin, SerialTXPin);

  Serial.println("Esp32 online");
  Serial2.println("Esp32 online");

  lastResponse = millis();
}

void loop() {
  currentTimeMicr = micros();
  currentTimeMillis = millis();
  if (Serial2.available() > 0) {
    Serial.printf("Last Response from pi %lu millis ago. \n", currentTimeMillis - lastResponse);
    lastResponse = currentTimeMillis;
    connection = true;
    String readse = readSerial2();
    Serial.printf("From Pi: %s\n", readse.c_str());
    detectPong(readse);
    if (readse == "Shutting down") {  //this stops the code from repeating the pinging forever. You would need to power off to reset this.
      piOff = true;
    }
  }

  if (Serial.available() > 0) {
    String sah = readSerial();
    Serial2.println(sah);
    Serial.println(sah);
    pingDetect(sah);
  }

  isPiThere();
  multiplePing();
}
