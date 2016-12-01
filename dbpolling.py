import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from lib_nrf24 import NRF24
import time
import spidev
import MySQLdb


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

#Database select
db = MySQLdb.connect("localhost","monitor","password","commands")
cur=db.cursor()



message = list("````````````````````````````````")
sendmessage = message
address = "" 
command = ""
data = "default"
dvaddress="0000"

while len(message) < 32:
    message.append(0)
    
while True:
	cur.execute("select * from module")
	for reading in cur.fetchall():
		
		if reading[1]==1:
			address=reading[0]
			cur.execute("select * from cmd")
			
			for cmd in cur.fetchall():
				if cmd[1]==1:
					command = cmd[0]
					cur.execute("select * from data")
					for dat in cur.fetchall():#########################################
						data=dat[0]#default olma durumu ile ilgili bir statement eklenecek

	sendmessage = dvaddress +'`'+ address +'`'+ command +'`'+ data +'`' #gonderilecek mesajin olusturulmasi
	print(sendmessage)				
	if sendmessage!=message:
	    
		start = time.time()
		radio.stopListening()
		radio.write(sendmessage)
		print("Sent the message: {}".format(sendmessage))
		radio.startListening() #pi starts to listen after sending the "message"
    
		while not radio.available(0):
			time.sleep(1/100)
                	if time.time() - start > 5:
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

	    	time.sleep(1)
	    	sendmessage=message
