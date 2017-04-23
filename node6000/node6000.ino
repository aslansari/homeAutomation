#include <SPI.h>
#include <RF24.h>

//ce , csn pins
RF24 radio(9,10);

#define ADDR 4
#define CMD 20
#define DATA 28
#define window 3
#define parent 0xF0F0F0F0E1LL 
#define alertPipe 0xc0c0c0c0a1LL
#define childA 0xF0F0A020E1LL
#define childB 0xF0F0B020E1LL
#define deviceaddr "6000"
/*    This module is one of the child of raspberryPi.
 *     1000 represents that the module is in the first layer of nodes
 *     each digit shows where module works on network
 *     for ex. first digit says it is the first module in the first layer
 *     if its '1B00' that module would be the second child module of 1000 
*/
String message="";
boolean wState;
boolean writeFlag;
boolean stateBuffer;
boolean wS;
boolean timeout;
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

  pinMode(window,INPUT);
  
}

void loop(){
  
  if(wState!=windowState()){
    Serial.println("debug1111");
    Serial.print("wstate: ");
    Serial.println(wState);
    delay(1000);
    stateBuffer = windowState();
    Serial.print("buffer: ");
    Serial.println(stateBuffer);
    if(wState!=stateBuffer){
      Serial.println("debug2222");
      radio.stopListening();
      cleanArrays();
      message = "6000";
      message.toCharArray(sender_address,sizeof(message));
      message = "0000";
      message.toCharArray(address,sizeof(message));
      message = "WINDOW";
      message.toCharArray(command,16);
      Serial.println("command: "+String(command));
      if(stateBuffer==1){
        message = "CLOSE";
      }
      else{
        message = "OPEN";
      }
      message.toCharArray(mdata,sizeof(message));
      writeFrame();
      radio.write(transmitMessage,sizeof(transmitMessage));
      Serial.println(transmitMessage);
//      wState = stateBuffer;
      Serial.print("wstate: ");
      Serial.println(wState);

      radio.startListening();
      time = millis();
      timeout = 0;
      while(!radio.available()){
        if(millis()>time + 1000){
          timeout = 1;
          break;
        }
      }

      if(!timeout){
        radio.read(receivedMessage,sizeof(receivedMessage));
        Serial.println(receivedMessage);
        readFrame();
        if(String(mdata)=="ACK"){
          wState = stateBuffer;
          Serial.print("wstate: ");
          Serial.println(wState);
        }
      }
    }
  }
  
  
  Serial.println("polling...");
  delay(500);
}

boolean windowState(){
  Serial.println("debug3333");
  wS = digitalRead(window);
  Serial.print("wS: ");
  Serial.println(wS);
  return wS;
  }


void writeFrame(){
  i=0;
  counter=i;
  for(int t=0;t<sizeof(transmitMessage);t++){
    transmitMessage[t]='\0';
  }
  while(address[i-counter]!='\0'){
    transmitMessage[i]=address[i-counter];
    i++;
  }
  transmitMessage[i]='`';
  i++;
  counter=i;
  while(sender_address[i-counter]!='\0'){
    transmitMessage[i]=sender_address[i-counter];
    i++;
  }
  transmitMessage[i]='`';
  i++;
  counter=i;
  while(command[i-counter]!='\0'){
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
  for(int t=0;t<sizeof(mdata);t++){
    mdata[t]='\0';
  }
  for(int t=0;t<sizeof(command);t++){
    command[t]='\0';
  }
  while(receivedMessage[i]!='`'){
    sender_address[i-counter]=receivedMessage[i];
    i++;
  }
  i++;// '`' karakteri geçiliyor
  counter=i;  //counter eşitlenerek address dizisinin ilk elemanindan atanmasi saglaniyor
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
void cleanArrays(){
  for(int t=0;t<sizeof(command);t++){
    command[t]='\0';
  }
  for(int t=0;t<sizeof(mdata);t++){
    mdata[t]='\0';
  }
}

