/*
<< MFRC522 RFID Kart Okuyucu ile Giriş Modülü >> 

* Çalışma Frekansı: 13.56 MHz
* Haberleşme Hızı: 424 kbit/s 
* Desteklenen Kart Tipleri: 
  ~mifare1 s50 ~mifare1 s70 ~mifare ultralight ~mifare pro ~ mifare desfire
  Pin Bağlantısı:
* MOSI: Pin 11 
* MISO: Pin 12 
* SCK: Pin 13 
* SS: Pin 10
* RST: Pin 9
*/
//SPI ve RFID kütüphaneleri
#include <SPI.h>
#include <RFID.h>
#include <RF24.h>
#include <avr/wdt.h>
#define SS_PIN 8
#define RST_PIN 7
#define DOOR_PIN 4
#define door_button 5

const int buzzer_1 =  2;
RF24 radio(9,10);
RFID rfid(SS_PIN, RST_PIN); 

//ce,csn pins


#define parent 0xF0F0F0F0E1LL
#define deviceaddr "5000"
// UID için Değişkenler:
    int serNum0;
    int serNum1;
    int serNum2;
    int serNum3;
    int serNum4;

char receivedMessage[32]={0};
char transmitMessage[32]={0};
char sender_address[5]={0};
char address[5]={0};
char command[17]={0};
char mdata[9]={0};
int i=0;
int counter=0;
String message="";
unsigned long time;
unsigned long radiotime;
boolean timeout = false;
boolean visitorIs = false; //false by default
void setup()
{ 
  wdt_enable(WDTO_2S);//wdt setup 2 sn
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  radio.openWritingPipe(parent);
  const uint64_t pipe = 0xE8E8F0F0E1LL;
  radio.openReadingPipe(1,pipe);
    
  radio.enableDynamicPayloads();
  radio.powerUp();

  pinMode(DOOR_PIN,OUTPUT);
  pinMode(door_button,INPUT);
  pinMode(buzzer_1, OUTPUT);
  Serial.begin(9600);
  SPI.begin(); 
  rfid.init();

  digitalWrite(DOOR_PIN,HIGH);
}

void loop()
{
  wdt_reset();
  if (rfid.isCard()) {
    digitalWrite(buzzer_1, HIGH);
    if (rfid.readCardSerial()) {
      // Kartık id'si son okutulan kart ile aynı mı?
      if (rfid.serNum[0] != serNum0
        || rfid.serNum[1] != serNum1
        || rfid.serNum[2] != serNum2
        || rfid.serNum[3] != serNum3
        || rfid.serNum[4] != serNum4
        || (millis()> time + 5000)
        ) {
        // Eğer Yeni Bir Kart Okutulduysa... 
        Serial.println(" ");
        Serial.println("Kart Bulundu");
        serNum0 = rfid.serNum[0];
        serNum1 = rfid.serNum[1];
        serNum2 = rfid.serNum[2];
        serNum3 = rfid.serNum[3];
        serNum4 = rfid.serNum[4];
        Serial.print("Kimlik: ");
                
        visitorIs = IDread();     
        printID();
        
        
        message.toCharArray(mdata,sizeof(message));
        message = "ID";
        message.toCharArray(command,sizeof(message));
        message = "0000";
        message.toCharArray(sender_address,sizeof(message));
        message = deviceaddr;
        message.toCharArray(address,sizeof(message));
        writeFrame();
        radio.stopListening();
        radio.openWritingPipe(parent);
        Serial.println(transmitMessage);
        radio.write(transmitMessage,sizeof(transmitMessage));

        radio.startListening();
  
        radiotime = millis();
        while(!radio.available()){
          if( millis() > radiotime + 1000 ){
            Serial.println("radio read timed out.");
            timeout = 1;
            break;
          }
        
        }
        wdt_reset();
        if(!timeout){
          radio.read(receivedMessage, sizeof(receivedMessage));
          Serial.println(receivedMessage);
          readFrame();
          Serial.println(String(mdata));
          Serial.println(visitorIs);
          
        }
        wdt_reset();
        radio.stopListening();
        //Door is opening
        if( visitorIs==1 && String(mdata)=="OK"){
          openDoor();
        }
        wdt_reset();
        radio.stopListening();     
        time = millis();
      }
      else{
        
       // Eğer aynı kart okutuluyorsa, id'yi tekrar basmak yerine
       //nokta basıyoruz.
        Serial.print(".");
      }
    }
    delay(200);
    digitalWrite(buzzer_1, LOW);
  }
  if(digitalRead(door_button)){
    digitalWrite(buzzer_1,HIGH);
    openDoor();
    digitalWrite(buzzer_1,LOW);
  }
  wdt_reset();
  
//  radio.startListening();
//  radiotime = millis();
//  while(!radio.available()){
//    if( millis() > radiotime + 500 ){
//      Serial.println("radio read timed out.");
//      timeout = 1;
//      break;
//    }
//  }
//
//  if(!timeout){
//    radio.read(receivedMessage, sizeof(receivedMessage));
//    Serial.println(receivedMessage);
//    readFrame();
//    Serial.println(String(mdata));
//    Serial.println(visitorIs);
//    radio.stopListening();
//    if(String(mdata)=="OPEN"){
//      message = "5000";
//      message.toCharArray(sender_address,sizeof(message));
//      message = "0000";
//      message.toCharArray(address,sizeof(message));
//      message = "DOOR";
//      message.toCharArray(command,sizeof(message));
//      message = "OPEN";
//      message.toCharArray(mdata,sizeof(message));
//      writeFrame();
//      radio.write(transmitMessage,sizeof(transmitMessage)); 
//    }
//    
//  }
//  wdt_reset();
//
//  if(String(mdata)=="OPEN"){
//    digitalWrite(buzzer_1,HIGH);
//    openDoor();
//    digitalWrite(buzzer_1,LOW);
//  }

  wdt_reset();
  rfid.halt();
  timeout=0;
}

void printID(){                
                Serial.println("Kart ID:");
                Serial.print("Dec: ");
    Serial.print(rfid.serNum[0],DEC);
                Serial.print(", ");
    Serial.print(rfid.serNum[1],DEC);
                Serial.print(", ");
    Serial.print(rfid.serNum[2],DEC);
                Serial.print(", ");
    Serial.print(rfid.serNum[3],DEC);
                Serial.print(", ");
    Serial.print(rfid.serNum[4],DEC);
                Serial.println(" ");
                        
                Serial.print("Hex: ");
    Serial.print(rfid.serNum[0],HEX);
                Serial.print(", ");
    Serial.print(rfid.serNum[1],HEX);
                Serial.print(", ");
    Serial.print(rfid.serNum[2],HEX);
                Serial.print(", ");
    Serial.print(rfid.serNum[3],HEX);
                Serial.print(", ");
            Serial.print(rfid.serNum[4],HEX);
                Serial.println(" ");
  
}
void openDoor(){
  digitalWrite(DOOR_PIN,LOW);
  delay(3000);
  digitalWrite(DOOR_PIN,HIGH);
}

boolean IDread(){
  if(serNum0==21 && serNum1==118 && serNum2==55 && serNum3==65 && serNum4==21){
    Serial.println("Furkan Ermanas YABANCI");
    message = "#1395";
    return true;
  }
  else if(serNum0==149 && serNum1==71 && serNum2==57 && serNum3==65 && serNum4==170){
    Serial.println("Aslan SARI");
    message = "#0617";
    return true;
  }
  else if(serNum0==10 && serNum1==192 && serNum2==14 && serNum3==49 && serNum4==245){
    Serial.println("Dergah Coskun YILDIZ");
    message = "#1907";
    return true;
  }
  else if(serNum0==212 && serNum1==156 && serNum2==222 && serNum3==164 && serNum4==50){
    Serial.println("Berk DEMIRKIRAN");
    message = "#3169";
    return true;
  }
  else if(serNum0==32 && serNum1==144 && serNum2==122 && serNum3==122 && serNum4==176){
    Serial.println("ADMIN");
    message = "#0001";
    return true;
  }
  else{
    Serial.println("Tanimsiz.");
    return false;
  }
}

void writeFrame(){
  int i=0;
  int  counter=i;
  for(int t=0;t<sizeof(receivedMessage);t++){
    receivedMessage[t]='\0';
  }
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
  for(int t=0;t<sizeof(mdata);t++){
    mdata[t]='\0';
  }
  for(int t=0;t<sizeof(command);t++){
    command[t]='\0';
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

