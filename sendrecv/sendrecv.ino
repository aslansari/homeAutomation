#include <SPI.h>
#include <RF24.h>

//ce , csn pins
RF24 radio(9,10);

#define ADDR 4
#define CMD 20
#define DATA 28

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
  char address[4]={0};
  char command[16]={0};
  char mdata[8]={0};
  if(radio.available()){
    radio.read(receivedMessage, sizeof(receivedMessage));
    Serial.println(receivedMessage);
    Serial.println("Turning off the radio.");
    radio.stopListening();
    /*
    String convertedMessage(receivedMessage);
    for(int i=0;i<=(sizeof(receivedMessage)-3);i++){
      convertedMessage[i]=receivedMessage[i+3];
    }
    Serial.println(convertedMessage);
    String stringMessage(convertedMessage);
    */

    for(int i=0;i<=ADDR;i++){
    	address[i]=receivedMessage[i];
    }
    for(int i=ADDR;i<=CMD;i++){
    	command[i-4]=receivedMessage[i];
    }
    for (int i = CMD; i <= DATA; i++)
    {
    	mdata[i-20]=receivedMessage[i];
    }
    if (stringMessage == "STRING"){
      Serial.println("Lools like they want a string");
      const char text[] = "Hello World!";
      radio.write(text,sizeof(text));
      Serial.println("We sent our message");
    }
  }
}

