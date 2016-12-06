#include <SPI.h>
#include <RF24.h>

//ce , csn pins
RF24 radio(9,10);

#define ADDR 4
#define CMD 20
#define DATA 28

#define parent 0xF0F0F0F0E1LL
#define childA 0xF0F0A010E1LL
#define childB 0xF0F0B010E1LL
#define deviceaddr "1000"
/*    This module is one of the child of raspberryPi.
 *     1000 represents that the module is in the first layer of nodes
 *     each digit shows where module works on network
 *     for ex. first digit says it is the first module in the first layer
 *     if its '1B00' that module would be the second child module of 1000 
*/

int i=0;
int counter=0;
float temp,temps;
boolean writeFlag;
char receivedMessage[32]={0};
char transmitMessage[32]={};
char address[5]={0};
char receiveAddress[5]={};
char command[17]={0};
char mdata[9]={0};
  
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

  if(radio.available()){
    radio.read(receivedMessage, sizeof(receivedMessage));
    Serial.println(receivedMessage);
    Serial.println("Turning off the radio.");
    radio.stopListening();
    i=0;
    counter=i;//i degiskeni counter degiskenine atanır ve while içinde i artarken counter sabit kalir 
    //ve dizinin ilk elemanindan atanmaya baslanir
    while(receivedMessage[i]!='`'){
      receiveAddress[i-counter]=receivedMessage[i];
      i++;
    }
    String receivingAddress = String(receiveAddress);
    Serial.println("receivedAddress"+receivingAddress);
    Serial.println("current i="+i);
    i++;
    counter=i;
    while(receivedMessage[i]!='`'){
      address[i-counter]=receivedMessage[i];
      i++;
    }
    String adres = String(address);
    Serial.println("Address"+adres);
    Serial.println("current i="+i);
    i++;
    counter=i;
    while(receivedMessage[i]!='`'){
      command[i-counter]=receivedMessage[i];
      i++;
    }
    String komut = String(command);
    Serial.println("Komut="+komut);
    Serial.println("current i="+i);
    i++;
    counter=i;
    while(receivedMessage[i]!='`'){
      mdata[i-counter]=receivedMessage[i];
      i++;
    }
    i=0;//mesaj parcalara ayrilarak farkli degiskenlerde saklaniyor
    
    if(address[0]=='1'&&address[1]=='0'&&address[2]=='0'&&address[3]=='0'){
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
    		Serial.println("adres bulunamadı");
    		break;
    	}
    }

    String commands = String(command);
    Serial.println(commands);
    if (commands == "GETTEMP"){
      Serial.println("Host asked for a temperature ");
      //converting temperature value to string
      String message = String(temp,DEC);
      message.toCharArray(mdata,sizeof(message));
      writeFrame();//data ve ardeslerin gonderilecek mesaja yazilmasi
      Serial.println(transmitMessage);
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

void writeFrame(){
  i=0;
  String debug = String(address);
  Serial.println(debug);
  counter=i;
  while(address[i-counter]!='\0'){
    transmitMessage[i]=address[i-counter];
    Serial.println(transmitMessage[i]);
    i++;
  }
  transmitMessage[i]='`';
  i++;
  counter=i;
  debug = String(receiveAddress);
  Serial.println(debug);
  while(receiveAddress[i-counter]!='\0'){
    transmitMessage[i]=receiveAddress[i-counter];
    Serial.println(transmitMessage[i]);
    i++;
  }
  transmitMessage[i]='`';
  i++;
  counter=i;
  debug = String(command);
  Serial.println(debug);
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
  for(int k=i;k<=32;k++){
    transmitMessage[k]='`';
  }
  i=0;
}

