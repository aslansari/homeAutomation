#include <SPI.h>
#include <RF24.h>

//ce , csn pins
RF24 radio(9,10);

#define ADDR 4
#define CMD 20
#define DATA 28

#define parent 0xF0F0F0F0E1LL
#define alertPipe 0xc0c0c0c0a1LL
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
int i=0;
int counter=0;
unsigned long time;

char receivedMessage[32]={0};
char transmitMessage[32]={0};
char sender_address[5]={0};
char address[5]={0};
char command[17]={0};
char mdata[9]={0};

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

  if(radio.available()){
    radio.read(receivedMessage, sizeof(receivedMessage));
    Serial.println(receivedMessage);
    Serial.println("Turning off the radio.");
    radio.stopListening();
    
    readFrame();	//read received Frame and assign in dedicated array
    String str_address = String(address);
    if(str_address=="2000"){
    	Serial.println("you are in the right node");
    }
    else if(str_address=="0000"){
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
    
    String str_command = String(command);	//transformation for if statement
    Serial.println(str_command);
    if (str_command == "GETTEMP"){
      Serial.println("Host asked for a temperature ");
      //Serial.println(temp);
      //converting temperature value to string and to char array
      String message = String(temp,DEC);
      message.toCharArray(mdata,sizeof(message));
      
      writeFrame();//data ve ardeslerin gonderilecek mesaja yazilmasi
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
  Serial.println(temp);
  
  if(temp>30){//SEND ALERT NOTIFICATION
    radio.stopListening();
    String sender = "2000";
    String rcver = "0000";
    String message = String(temp,DEC);
    String str_command = "ALERT";
    sender.toCharArray(address,sizeof(sender));
    rcver.toCharArray(sender_address,sizeof(sender));
    str_command.toCharArray(command,sizeof(str_command));
    message.toCharArray(mdata,sizeof(message));
    writeFrame();
    
    radio.openWritingPipe(parent);
    radio.write(transmitMessage,sizeof(transmitMessage));
    Serial.println(transmitMessage);
    radio.startListening();
    time = micros();
    
  }
  delay(500);
}

float getTemp(void){
	//converting analog input to temperature value
	//used LM35 for temp sensor
  	//Serial.println("messuring temperature");
	temps = analogRead(A2);
  //Serial.println(temps);
	temps = (temps*5000)/1023;
	temps = temps/10;
	return temps;
 
}

void writeFrame(){
  i=0;
  counter=i;
  while(address[i-counter]!='\0'){
    transmitMessage[i]=address[i-counter];
    Serial.println(transmitMessage[i]);
    i++;
  }
  transmitMessage[i]='`';
  i++;
  counter=i;
  while(sender_address[i-counter]!='\0'){
    transmitMessage[i]=sender_address[i-counter];
    Serial.println(transmitMessage[i]);
    i++;
  }
  transmitMessage[i]='`';
  i++;
  counter=i;
  while(command[i-counter]!='\0'){
    Serial.println(command[i-counter]);
    transmitMessage[i]=command[i-counter];
    i++;
  }
  transmitMessage[i]='`';
  i++;
  counter=i;
  while(mdata[i-counter]!='\0'){
    transmitMessage[i]=mdata[i-counter];
    i++;
  }
  transmitMessage[i]='`';
  i=0;
}

void readFrame(){
	i=0;
	counter=i;
	while(receivedMessage[i]!='`'){
		sender_address[i-counter]=receivedMessage[i];
		i++;
	}
	i++;// '`' karakteri geçiliyor
	counter=i;	//counter eşitlenerek address dizisinin ilk elemanindan atanmasi saglaniyor
	while(receivedMessage[i]!='`'){
		address[i-counter]=receivedMessage[i];
		i++;
	}
	i++;
	counter=i;
	while(receivedMessage[i]!='`'){
		command[i-counter]=receivedMessage[i];
		i++;
	}
	i++;
	counter=i;
	while(receivedMessage[i]!='`'){
		mdata[i-counter]=receivedMessage[i];
		i++;
	}

}

