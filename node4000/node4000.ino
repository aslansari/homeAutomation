#include <SPI.h>
#include <RF24.h>
#include <IRremote.h>

#define RECV_PIN 5

#define parent 0xE8E8F0F0E1LL
#define childA 0xF0F0A040E1LL
#define childB 0xF0F0B040E1LL
#define deviceaddr "4000"
//ce , csn pins
RF24 radio(9,10);

IRrecv irrecv(RECV_PIN);

decode_results results;

int i=0;
int counter=0;
char receivedMessage[32]={0};
char transmitMessage[32]={0};
char sender_address[5]={0};
char address[5]={0};
char command[17]={0};
char mdata[9]={0};

String str_data = "";
String str_cmd = "";
String str_address = "";

void setup() {
  while(!Serial);
  Serial.begin(9600);
  
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  radio.openWritingPipe(parent);
  const uint64_t pipe = 0xF0F0A030E1LL;
  radio.openReadingPipe(1,pipe);
    
  radio.enableDynamicPayloads();
  radio.powerUp();

  irrecv.enableIRIn();  //start the receiver
}

void loop() {
  // put your main code here, to run repeatedly:
  if(irrecv.decode(&results)){
  	int button = translateIR();

  	switch(button){
  		case 201: 
  			str_address = "3000";
  			str_cmd = "LIGHT";
  			str_data = "ON";
  			break;
  		case 203:
  			str_address = "3000";
  			str_cmd = "LIGHT";
  			str_data = "OFF";
  			break;
  		default:
  			str_address = "";
  			str_cmd = "";
  			str_data = "";
  	}
    String str_pi ="0000";
  	str_pi.toCharArray(address,sizeof(str_pi));
  	str_address.toCharArray(sender_address,sizeof(str_address));
  	str_cmd.toCharArray(command,sizeof(str_cmd));
  	str_data.toCharArray(mdata,sizeof(mdata));
  	writeFrame();

  	radio.openWritingPipe(parent);
  	radio.write(transmitMessage,sizeof(transmitMessage));
    Serial.println(transmitMessage);

    irrecv.resume();  //receive the next value
  }
}

int translateIR() // takes action based on IR code received
// describing Remote IR codes 
{
	int basilan_buton=0;
  switch(results.value)
  {
    case 0xFF629D: Serial.println(" FORWARD"); basilan_buton=101; break; //basılan buton değişkenine atanan değerin yüzler basamağı hangi satırda 
    case 0xFF22DD: Serial.println(" LEFT");    basilan_buton=201; break; //diğer iki rakam da kaçıncı buton olduğunu gösteriyor
    case 0xFF02FD: Serial.println(" -OK-");    basilan_buton=202; break;
    case 0xFFC23D: Serial.println(" RIGHT");   basilan_buton=203; break;
    case 0xFFA857: Serial.println(" REVERSE"); basilan_buton=301; break;
    case 0xFF6897: Serial.println(" 1");       basilan_buton=401; break;
    case 0xFF9867: Serial.println(" 2");       basilan_buton=402; break;
    case 0xFFB04F: Serial.println(" 3");       basilan_buton=403; break;
    case 0xFF30CF: Serial.println(" 4");       basilan_buton=501; break;
    case 0xFF18E7: Serial.println(" 5");       basilan_buton=502; break;
    case 0xFF7A85: Serial.println(" 6");       basilan_buton=503; break;
    case 0xFF10EF: Serial.println(" 7");       basilan_buton=601; break;
    case 0xFF38C7: Serial.println(" 8");       basilan_buton=602; break;
    case 0xFF5AA5: Serial.println(" 9");       basilan_buton=603; break;
    case 0xFF42BD: Serial.println(" *");       basilan_buton=701; break;
    case 0xFF4AB5: Serial.println(" 0");       basilan_buton=702; break;
    case 0xFF52AD: Serial.println(" #");       basilan_buton=703; break;
    case 0xFFFFFFFF: Serial.println(" REPEAT");basilan_buton=0;    break;  
    default: 
    Serial.println(" other button   "); basilan_buton=0;
    
  }// End Case
  
  delay(500); // Do not get immediate repeat
  return basilan_buton;
} //END translateIR

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
    Serial.println(mdata[i-counter]);
    transmitMessage[i]=mdata[i-counter];
    i++;
  }
  for(int k=i;k<=32;k++){
    transmitMessage[k]='`';
  }
  i=0;
}

void readFrame(){
  for(int t=0;t<sizeof(mdata);t++){
    mdata[t]='\0';
  }
  i=0;
  counter=i;
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

