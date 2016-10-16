#include <SPI.h>
#include <RF24.h>

//ce , csn pins
RF24 radio(9,10);

void setup(){
  while(!Serial);
  Serial.begin(9600);
  
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  radio.openWritingPipe(0xF0F0F0F0E1LL);
  const uint64_t pipe = 0xE8E8F0F0E1LL;
  radio.openReadingPipe(1,pipe);
    
  radio.enableDynamicPayloads();
  radio.powerUp();
 
}

void loop(){
  radio.startListening();
  Serial.println("Starting Loop. Radio on.");
  char receivedMessage[32]={0};
  if(radio.available()){
    radio.read(receivedMessage, sizeof(receivedMessage));
    Serial.println(receivedMessage);
    Serial.println("Turning off the radio.");
    radio.stopListening();

    String stringMessage(receivedMessage);

    if (stringMessage == "GETSTRING"){
      Serial.println("Lools like they want a string");
      const char text[] = "Hello World!";
      radio.write(text,sizeof(text));
      Serial.println("We sent our message");
    }
  }
}

