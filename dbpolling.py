# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
from lib_nrf24 import NRF24
import time
import spidev
import MySQLdb
import os
import ftplib
import functions
import datetime

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

now = datetime.datetime.now() #belirli aralıklarla çekilen fotoğraflar için tanımlamalar
now_hour = now.hour
then_hour = now.hour
now_min = now.minute
if now_min<55:
	then_min = now_min + 5	#her 5 dakikada bir fotoğraf çekilecek
else: 
	then_min = now_min - 55
	then_hour = now_hour + 1
    
while True:
	dvaddress = '0000'
	address = ""
	command = ""
	data = "default"

	db = MySQLdb.connect("localhost","monitor","password","commands")
	cur=db.cursor()

	cur.execute("select * from module")
	for reading in cur.fetchall():
				
		if reading[1]==1:
			
			address=reading[0]
			cur.execute("select * from cmd")
			print(address)
			for cmd in cur.fetchall():
				if cmd[1]==1:
					
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
			
								
			splitFrame = string.split("`") # gelen mesajı ` karakterine göre parçalıyoruz
			
			dvaddress = splitFrame[0]
			address = splitFrame[1]
			command = splitFrame[2]
			data = splitFrame[3]
			
			if(command=="GETTEMP"):
				print("writing temp data on database")
				tempdb = MySQLdb.connect('localhost','monitor','password','temps')
				temp_cur = tempdb.cursor()
				str_db = "insert into tempdat values(CURRENT_DATE(),NOW(),"
				str_db = str_db + "\'" + dvaddress + "\'" +","
				str_db = str_db + data + ")" #gelen datalar ile mesaj oluşturuldu
				print(str_db)
				try:
					temp_cur.execute(str_db) #bilgiler database'e giriliyor
					tempdb.commit()
					print("data committed.")
					
					str_db = "update module SET flag=0 where node="
					str_db = str_db + "\'" + dvaddress + "\'"					
					print(str_db)
	
					try:
						cur.execute(str_db)
						db.commit()
						print("flags are down.")
					except:
						db.rollback()
						print("database rolled back")
					cur.execute("update cmd SET flag=0 where command='GETTEMP'")
					db.commit()
					address = ""
					command = ""
					data = ""
					print("all flags are zero")
					print("address=",address," command=",command," data=",data)
				except:
					tempdb.rollback()
					print("database rolledback. Couldn't commit")
	   	sendmessage="0000```default`"
	time.sleep(1)

	now = datetime.datetime.now()
	now_min = now.minute
	now_hour = now.hour
	print("then hour= ", then_hour)
	print("now hour= ", now_hour)
	print("now minute= ", now_min)
	print("then minute= ", then_min)	
	
	if ((now_min>=then_min) & (then_hour==now_hour)):
		functions.sec_photo()
		
		if now_min<=55:
			then_min = now_min + 5
		else:
			then_min = now_min - 55
			then_hour = now.hour + 1


