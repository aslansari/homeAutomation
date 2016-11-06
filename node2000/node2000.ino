#include <SPI.h>
#include <RF24.h>

//ce , csn pins
RF24 radio(9,10);

#define ADDR 4
#define CMD 20
#define DATA 28

#define parent 0xF0F0F0F0E1LL
#define childA 0xF0F0A020E1LL
#define childB 0xF0F0B020E1LL
#define deviceaddr "2000"
/*    This module is one of the child of raspberryPi.
 *     1000 represents that the module is in the first layer of nodes
 *     each digit shows where module works on network
 *     for ex. first digit says it is the first module in the first layer
 *     if its '1B00' that module would be the second child module of 1000 
*/

float temp,temps;
boolean writeFlag;

void setup(){
  while(!Serial);
  Serial.begin(9600);
  
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  radio.openWritingPipe(parent);
  const uint64_t pipe = 0xE8E8F0F0E1LL;
  radio.openReadingPipe(1,pipe);
    
  radio.enableDynamicPayloads();
  radio.powerUp();

  
}

void loop(){
  radio.startListening();
  Serial.println("Starting Loop. Radio on.");
  char receivedMessage[32]={0};
  char transmitMessage[32]={0};
  char address[5]={0};
  char command[17]={0};
  char mdata[9]={0};
  if(radio.available()){
    radio.read(receivedMessage, sizeof(receivedMessage));
    Serial.println(receivedMessage);
    Serial.println("Turning off the radio.");
    radio.stopListening();
    
    for(int i=0;i<ADDR;i++){
      if(receivedMessage[i]!='`')//yazılı karakter dışındaki karakterler diziye atanır
      address[i]=receivedMessage[i];
    }
    for(int i=ADDR;i<CMD;i++){
      if(receivedMessage[i]!='`')//yazılı karakter dışındaki karakterler command dizisine atanır
      command[i-4]=receivedMessage[i];
    }
    for (int i = CMD; i < DATA; i++)
    {
      if(receivedMessage[i]!='`')//yazılı karakter dışındaki karakterler diziye atanır
      mdata[i-20]=receivedMessage[i];
    }
    //
    if(address[0]=='2'&&address[1]=='0'&&address[2]=='0'&&address[3]=='0'){
    	Serial.println("you are in the right node");
    }
    else if(address[0]=='0'&&address[1]=='0'&&address[2]=='0'&&address[3]=='0'){
    	Serial.println("message is sending to raspverri pi");
    	radio.openWritingPipe(parent);
    	radio.write(receivedMessage,sizeof(receivedMessage));
    }
    else{
    	for(int i=0;i<=3;i++){
    		Serial.println(address[i]);
    	}
    	switch (address[1]){
    		case 'A':
        Serial.println("childA data sending..");
    		radio.stopListening();
    		radio.openWritingPipe(childA);
    		radio.write(receivedMessage,sizeof(receivedMessage));
        Serial.println("childA data has sent..");
    		break;
    		case 'B':
    		radio.openWritingPipe(childB);
    		radio.write(receivedMessage,sizeof(receivedMessage));
    		break;
    		default:
    		Serial.println("address not found");
    		break;
    	}
    }
    
    String commands = String(command);
    Serial.println(commands);
    if (commands == "GETTEMP"){
      Serial.println("Host asked for a temperature ");
      //Serial.println(temp);
      //converting temperature value to string
      String message = String(temp,DEC);
      message.toCharArray(transmitMessage,sizeof(message));
      //Serial.println(transmitMessage);
      radio.openWritingPipe(parent);
      writeFlag = radio.write(transmitMessage,sizeof(transmitMessage));
      if(writeFlag){// Acknowledge flag for transmitting data
      	Serial.println("Data sent succesfully.");
      	writeFlag = 0;
      }
    }
  }
  //temp data messured in every loop
  temp = getTemp();
}

float getTemp(void){
	//converting analog input to temperature value
	//used LM35 for temp sensor
  	//Serial.println("messuring temperature");
	temps = analogRead(A2);
  	//Serial.println(temps);
	temps = (temps*5000)/1023;
	temps = temps/10;
 	//Serial.println("Temperature ="+temps);
	return temps;
}
