#include <SPI.h>
#include <RF24.h>

//ce , csn pins
RF24 radio(9,10);

#define ADDR 4
#define CMD 20
#define DATA 28

#define parent 0xE8E8F0F0E1LL
#define child1 0xF010A010E1LL
#define child2 0xF010A010E1LL
#define deviceaddr "1A00"
/*    This module is one of the child of raspberryPi.
 *     1000 represents that the module is in the first layer of nodes
 *     each digit shows where module works on network
 *     for ex. first digit says it is the first module in the first layer
 *     if its '1B00' that module would be the second child module of 1000 
*/
void setup(){
  while(!Serial);
  Serial.begin(9600);
  
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  radio.openWritingPipe(0xF0F0F0F0E1LL);
  const uint64_t pipe = 0xF0F0A010E1LL;
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

    if(address=="1A00"){
    	println("you are in the right node");
    	String stringMessage(command);
    	if (stringMessage == "GETSTRING"){
      		Serial.println("Lools like they want a string");
      		const char text[] = "0000HELLOWORLD";
      		radio.write(text,sizeof(text));
      		Serial.println("We sent our message");
    	}
    }
    else if(adress=="0000"){
    	println("message is sending to raspverri pi");
    	radio.openWritingPipe(parent);
    	radio.write(receivedMessage,sizeof(receivedMessage));
    }
    else{
    	for(int i=0;i<=3;i++){
    		println(address[i]);
    	}
    	switch (address[2]){
    		case '1':
    		radio.openWritingPipe(child1);
    		radio.write(receivedMessage,sizeof(receivedMessage));
    		break;
    		case '2':
    		radio.openWritingPipe(child2);
    		radio.write(receivedMessage,sizeof(receivedMessage));
    		break;
    		default:
    		println("adres bulunamadı");
    		break;
    	}
    }
    /*
    if (stringMessage == "STRING"){
      Serial.println("Lools like they want a string");
      const char text[] = "Hello World!";
      radio.write(text,sizeof(text));
      Serial.println("We sent our message");
    }
    */
  }
}



