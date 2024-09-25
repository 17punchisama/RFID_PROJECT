#include <SPI.h> 
#include <MFRC522.h> 

#define SS_PIN 5   // SDA
#define RST_PIN 9  // RST

MFRC522 rfid(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(115200);
  SPI.begin();      // Initiate SPI bus
  rfid.PCD_Init();  // Initiate MFRC522
  
  Serial.println("Place your card/tag near the RFID reader...");
}

void loop() {
  // Look for new cards
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }
  // Select one of the cards
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  // Print UID
  Serial.print("UID tag : ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(rfid.uid.uidByte[i], HEX);
  }
  Serial.println();
  delay(1000);
}
