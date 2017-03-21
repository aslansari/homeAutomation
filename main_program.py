#!/usr/bin/env python
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
import mailnotification

pipes=[[0xE8, 0xE8, 0xF0, 0xF0,0xE1],[0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]

radio = NRF24(GPIO, spidev.SpiDev()) #Radio nesnesi tanımlandı
radio.begin(0,25)
#radio config
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
alert_time = now
if now_min<55:
	then_min = now_min + 5	#her 5 dakikada bir fotoğraf çekilecek
else: 
	then_min = now_min - 55
	if now_hour == 23:
		then_hour = 0	
	else:
		then_hour = now_hour + 1

def getTemp():
    sendmessage = "0000`2000`GETTEMP``"
    start = time.time()
    radio.stopListening()
    radio.write(sendmessage)
    print("Sent the message: {}".format(sendmessage))
    radio.startListening() #pi starts to listen after sending the "message"
    toFlag=0
    while not radio.available(0):
        time.sleep(1/100)
    	if time.time() - start > 2:
            print("Timed out.")
	    toFlag = 1
            break

    if not toFlag == 1:

    	receivedMessage = []
    	del receivedMessage[:]
    	radio.read(receivedMessage, radio.getDynamicPayloadSize())
    	print("Received:{}".format(receivedMessage))
    	print("Translating our received message into unicode characters..")
    	string=""
    	for n in receivedMessage:
    	    if(n >= 32 and n <= 126):
        	    string +=chr(n)
    	print("Our received message decodes to: {}".format(string))
    	if string != "":			
    		splitFrame = string.split("`") # gelen mesajı ` karakterine göre parçalıyoruz
				
		dvaddress = splitFrame[0]
		ddress = splitFrame[1]
		command = splitFrame[2]
		data = splitFrame[3]
				
		if(command=="GETTEMP"):
			print("writing temp data on database")
			tempdb = MySQLdb.connect('localhost','monitor','password','sensors')
			temp_cur = tempdb.cursor()
			str_db = "insert into tempdat values(CURRENT_DATE(),NOW() + INTERVAL 1 HOUR,"
			str_db = str_db + "\'" + dvaddress + "\'" +","
			str_db = str_db + data + ")" #gelen datalar ile mesaj oluşturuldu
			print(str_db)
			try:
				temp_cur.execute(str_db) #bilgiler database'e giriliyor
				tempdb.commit()
				address = ""
				command = ""
				data = ""
				print("all flags are zero")
				print("address=",address," command=",command," data=",data)
			except:
				tempdb.rollback()
				print("database rolledback. Couldn't commit")
	

    
while True:
	dvaddress = '0000'
	address = ""
	command = ""
	data = "default"
#incoming messages from slaves
	radio.stopListening()
	radio.startListening()
	start = time.time()
	messageFlag = 1
	while not radio.available(0):
		time.sleep(1/100)
		if time.time() - start >0.5:
			print "No message received."
			messageFlag = 0
			break
	if(radio.available()):
		rcvMessage = []
		del rcvMessage[:]
		radio.read(rcvMessage, radio.getDynamicPayloadSize())
		print "rcvmessage"
		print("Received:{}".format(rcvMessage))
		rcvString = ""
		for n in rcvMessage:
			if(n >= 32 and n<=126):
				rcvString += chr(n)
		
		rcvSplitFrame = rcvString.split("`")
		
		dvaddress = rcvSplitFrame[0]
		address = rcvSplitFrame[1]
		command = rcvSplitFrame[2]
		data = rcvSplitFrame[3]
		msg_time = datetime.datetime.now()
		
		if(command == "ALERT"):
                        if((msg_time.year>alert_time.year) | (msg_time.month>alert_time.month) | (msg_time.day>=alert_time.day)):
                                if((msg_time.hour==alert_time.hour) & (msg_time.minute>alert_time.minute+5)):
                                        alert_time = msg_time
                                        mailnotification.sendMail()
				elif(msg_time.hour>alert_time.hour):
					alert_time = msg_time
					mailnotification.sendMail()	
##############################
	db = MySQLdb.connect("localhost","monitor","password","commands")
	cur=db.cursor()

	cur.execute("select * from module")
	for reading in cur.fetchall():
				
		if reading[1]==1:
			address=reading[0]
			time.sleep(1/100) #sleep for 10ms
			cur.execute("select * from cmd")
			print(address)
			for cmd in cur.fetchall():
				if cmd[1]==1:
					
					command = cmd[0]
					time.sleep(1/100) #sleep for 10ms
					cur.execute("select * from data")
					print(command)
					for dat in cur.fetchall():#########################################
						dataFlag=dat[2]#default olma durumu ile ilgili bir statement eklenecek
						if dataFlag==1:
							data=dat[1]

	sendmessage = dvaddress +'`'+ address +'`'+ command +'`'+ data +'`' #gonderilecek mesajin olusturulmasi
	print(sendmessage)

#	if sendmessage != "0000```default`":
#		db = MySQLdb.connect("localhost","monitor","password","commands")
#		cur = db.cursor()
#		str_db = "insert into cmdqueue (command,flag) values "
#		str_db = str_db + "(\'" + sendmessage + "\'"
#		str_db = str_db + ",1)"
#		print str_db
#		cur.execute(str_db)
#		db.commit()
#		functions.setFlagZero() #command flags set to zero after command is added to command queue	

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
    			
			toFlag = 0
			while not radio.available(0):
				time.sleep(1/100)
               			if time.time() - start > 1:
                   			print("Timed out.")
					toFlag = 1
					break
			
			
			if not toFlag == 1:
			
            			receivedMessage = []
				del receivedMessage[:]
    	    			radio.read(receivedMessage, radio.getDynamicPayloadSize())
				print "dbrecvMessage"
	    			print("Received:{}".format(receivedMessage))
				print("Translating our received message into unicode characters..")
	    			string=""
		
	    			for n in receivedMessage:
	        			if(n >= 32 and n <= 126):
	        				string +=chr(n)
	    			print("Our received message decodes to: {}".format(string))
			
			
				if string != "":	
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
	
					if command=="LIGHT":
						if data =="ACK":
							print "light turned on succesfully"
							db = MySQLdb.connect('localhost','monitor','password','commands')
							cur = db.cursor()
							cur.execute("update cmd SET flag=0 where flag=1")
							cur.execute("update data SET flag=0 where flag=1")
							cur.execute("update data SET data='default' where id=1")
	
							str_db = "update module SET flag=0 where node="
							str_db = str_db + "\'" + dvaddress + "\'"
							cur.execute(str_db)
							db.commit()
							data = ""
	
						if data == "NACK":
							print "Attemp failed!"
							data = ""














	   	sendmessage="0000```default`"
		string=""
	time.sleep(1/10)
	now = datetime.datetime.now()
	now_min = now.minute
	now_hour = now.hour
	print("then hour= ", then_hour)
	print("now hour= ", now_hour)
	print("now minute= ", now_min)
	print("then minute= ", then_min)	
	
	if ((now_min>=then_min) & (then_hour==now_hour)):
		functions.sec_photo()
		getTemp()		
		if now_min<55:
			then_min = now_min + 5
		else:
			then_min = now_min - 55
			if now_hour ==23:
				then_hour = 0
			else:
				then_hour = now_hour + 1


