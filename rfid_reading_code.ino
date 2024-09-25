#include <SPI.h> 
#include <MFRC522.h> 
#include <WiFi.h>
#include <PubSubClient.h>

#define SS_PIN 5   // SDA
#define RST_PIN 9  // RST

MFRC522 rfid(SS_PIN, RST_PIN);  // Create MFRC522 instance

String rfidUID = "";  // Variable to store the RFID UID

//=================================================================================================
WiFiClient espClient;                     // Create WiFi client
PubSubClient client(espClient);           // Create MQTT client
//=================================================================================================
const char* ssid = "wifi_name";             // WiFi name
const char* password = "wifi_password";       // WiFi password
//=================================================================================================
const char* mqtt_broker = "broker.hivemq.com";  // IP of MQTT server
const int mqtt_port = 1883;                // Port of MQTT server
//=================================================================================================

void setup_wifi() { // Connect to WiFi
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char *topic, byte *payload, unsigned int length) {  //ฟังก์ชั่นsubscribe
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  for (int i = 0; i < length; i++)          //รับค่าโดยการปริ้นอักษรที่ละตัวออกมา เป็น char
    Serial.print((char) payload[i]);
  Serial.println();
  Serial.println("-----------------------");
}

void reconnect() { // Connect to MQTT
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
  while (!client.connected()) {
    String client_id = "esp32-client-";
    client_id += String(WiFi.macAddress());
    Serial.printf("The client %s connects to the public mqtt broker\n", client_id.c_str());
    if (client.connect(client_id.c_str()))
      Serial.println("Public MQTT broker connected");
    else {
      Serial.print("Failed with state ");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  SPI.begin();      // Initiate SPI bus
  rfid.PCD_Init();  // Initiate MFRC522
  setup_wifi(); // Connect to WiFi
  reconnect();  // Connect to MQTT
  client.subscribe("topic"); // Subscribe to topic
  
  Serial.println("Place your card/tag near the RFID reader...");
}

void loop() {

  client.loop();
  // Look for new cards
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }
  // Select one of the cards
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  // Clear the previous UID
  rfidUID = "";

  // Store and print UID
  Serial.print("UID tag : ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    // Append each byte to rfidUID variable
    rfidUID += String(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
    rfidUID += String(rfid.uid.uidByte[i], HEX);
  }

  // Convert rfidUID to uppercase
  rfidUID.toUpperCase();

  // Print stored UID
  Serial.println(rfidUID);

  delay(1000);

  client.publish("topic", rfidUID.c_str());
}
