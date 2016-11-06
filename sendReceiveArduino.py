import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from lib_nrf24 import NRF24
import time
import spidev



pipes=[[0xE8, 0xE8, 0xF0, 0xF0,0xE1],[0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0,25)

radio.setPayloadSize(32)
radio.setChannel(0x76)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MIN)

radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1,pipes[1])
radio.printDetails()
#radio.startListening() #pi is in master role so it doesnt need to listen at start

message = list("1A00GETTEMP")
while len(message) < 32:
    message.append(0)
    
while True:
    start = time.time()
    radio.write(message)
    print("Sent the message: {}".format(message))
    radio.startListening() #pi starts to listen after sending the "message"
    
    while not radio.available(0):
        time.sleep(1/100)
        if time.time() - start > 2:
            print("Timed out.")
            break

    receivedMessage=[]
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
    print("Received:{}".format(receivedMessage))

    print("Translating our received message into unicode characters..")
    string=""

    for n in receivedMessage:
        if(n >= 32 and n <= 126):
            string +=chr(n)
    print("Our received message decodes to: {}".format(string))

    radio.stopListening() #stopped listening because you cant send a message when you are listening
    time.sleep(1)
