import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from lib_nrf24 import NRF24
import time
import spidev
import MySQLdb
import os
import ftplib
import functions

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
global photo_counter
photo_counter = 1

sendmessage = message
while len(message) < 32:
    message.append(0)
    
while True:
	db = MySQLdb.connect("localhost","monitor","password","commands")
	cur=db.cursor()

	cur.execute("select * from module")
	for reading in cur.fetchall():
		print("fordebug")		
		if reading[1]==1:
			print("debug1")
			address=reading[0]
			cur.execute("select * from cmd")
			print(address)
			for cmd in cur.fetchall():
				if cmd[1]==1:
					print("debug2")
					command = cmd[0]
					cur.execute("select * from data")
					print(command)
					for dat in cur.fetchall():#########################################
						dataFlag=dat[1]#default olma durumu ile ilgili bir statement eklenecek
						if dataFlag==1:
							data=dat[0]

	sendmessage = dvaddress +'`'+ address +'`'+ command +'`'+ data +'`' #gonderilecek mesajin olusturulmasi
	print(sendmessage)				
	if sendmessage!="0000```default`":
	    
				
		if(address=="0000"):	#address of raspberry pi
			if(command=="CAPTURE"):#requested duty
				functions.take_photo(photo_counter)
				photo_counter+=1
				print("photo counter = ",photo_counter)
				if photo_counter>=6:
					photo_counter = 1
				try:
					cur.execute("update module SET flag=0 where node='0000'")
					cur.execute("update cmd SET flag=0 where command='CAPTURE'")
					db.commit()
					address=""
					command=""
					print("flags resetted")
				except:
					db.rollback()
					print("failed to commit")

				
			
		else:	#send message via radio if address is not pi's
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
			
			splitFrame = receivedMessage.split('`') # gelen mesajı ` karakterine göre parçalıyoruz

			address = splitFrame[1]
			command = splitFrame[2]
			data = splitFrame[3]
				
	   	sendmessage=message
	time.sleep(1)
