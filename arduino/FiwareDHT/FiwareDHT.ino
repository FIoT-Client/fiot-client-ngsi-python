#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <dht.h>

// Update these with values suitable for your network.
byte mac[]    = {  0xDE, 0xED, 0xBA, 0xFE, 0xFE, 0xED };
IPAddress ip(10, 7, 174, 14);
IPAddress server(10, 7, 49, 20);

EthernetClient ethClient;
PubSubClient client(ethClient);

dht DHT;

#define DHT21_PIN 2

void publishMeasurements() {
  char strHumidity[6];
  char strTemperature[6];

  char humidityPayloadBuf[20];
  char temperaturePayloadBuf[20];

  int chk = DHT.read21(DHT21_PIN);
  switch (chk){
    case DHTLIB_OK:
      dtostrf(DHT.humidity, 4, 2, strHumidity);
      dtostrf(DHT.temperature, 4, 2, strTemperature);

      sprintf(humidityPayloadBuf, "h|%s", strHumidity);
      sprintf(temperaturePayloadBuf, "t|%s", strTemperature);

      Serial.print(humidityPayloadBuf);
      Serial.print(", ");
      Serial.println(temperaturePayloadBuf);

      client.publish("/4jggokgpepnvsb2uv4s40d59ov1/STELA_DHT/attrs", humidityPayloadBuf);
      client.publish("/4jggokgpepnvsb2uv4s40d59ov1/STELA_DHT/attrs", temperaturePayloadBuf);

      delay(60000);
      break;
    default:
      Serial.println("Failed to read sensor. Trying again in 2 seconds.");
      delay(10000);
      break;
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Connecting to server...");
    if (!client.connect("arduinoClient")) {
      Serial.println("Connection failed. Trying again in 2 seconds.");
      delay(2000); // Wait until try again
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000);

  client.setServer(server, 1883);
  Ethernet.begin(mac, ip);
  delay(1500);  // Allow the hardware to sort itself out
}

void loop() {
  if (client.connected()){
    publishMeasurements();
  } else {
    reconnect();
  }
//  client.loop();
}
