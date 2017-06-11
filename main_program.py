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
alert_time = datetime.datetime.now()	

if now_min<55:
	then_min = now_min + 5	#her 5 dakikada bir fotoğraf çekilecek
else: 
	then_min = now_min - 55
	if now_hour == 23:
			then_hour = 0	
	else:
		then_hour = now_hour + 1

def nodeAccess(accdvaddress,accaddress,acccommand,accdata):
        sendmessage = accdvaddress + '`' + accaddress + '`' + acccommand + '`' + accdata + '`'
        start = time.time()
        radio.stopListening()
        radio.write(sendmessage)
        print sendmessage
        print("Sent the message: {}".format(sendmessage))
        radio.startListening()
        toFlag = 0

        while not radio.available(0):
		time.sleep(1/100)
		if time.time() - start > 2:
			print("Communication timed out.")
			toFlag = 1
			return 0
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
				
		return splitFrame
                

	
def getTemp(self):
        if self == "":
                targetNode = "1000"
        else:
                targetNode = self
	msgtoSend = "0000`"
	msgtoSend = msgtoSend + targetNode +"`GETTEMP``"
	print msgtoSend
	start = time.time()
	radio.stopListening()
	radio.write(msgtoSend)
	print("Sent the message: {}".format(msgtoSend))
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
			str_db = "insert into tempdat values(CURRENT_DATE(),NOW(),"
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
	
def fetchCommand():
    	db = MySQLdb.connect("localhost","monitor","password","commands")
	cur=db.cursor()

        cur.execute("select * from cmdready")
        for reading in cur.fetchall():
                if reading[1]==1:
                        print "Command is ready to send"
                        
                        cur.execute("select * from module")
                        for reading in cur.fetchall():
				if reading[1]==1:
                                        address=reading[0]

                                        cur.execute("select * from cmd")
                                        print(address)
                                        for cmd in cur.fetchall():
                                                if cmd[1]==1:
                                                        command = cmd[0]
                                                        print(command)
                                                        cur.execute("select * from data")
                                                        for dat in cur.fetchall():#########################################
                                                              	dataFlag=dat[2]#default olma durumu ile ilgili bir statement eklenecek
                                                        	if(dataFlag==1):
                                                                	data=dat[1]
									print data
									break
                                                                else:
									data="default"

                        sendmessage = dvaddress +'`'+ address +'`'+ command +'`'+ data +'`' #gonderilecek mesajin olusturulmasi
##                        print(sendmessage)
                        return sendmessage
                else:
                        return ""

def alertProcess():
        print "Sending e-mail notification"
#        mailnotification.sendMail() #sends mail about the alert situation
        for x in range(3):
                success = nodeAccess("0000","3000","LIGHT","ON")
                if success!=0:
                        break
        for x in range(3):
                success = nodeAccess("0000","5000","DOOR","OPEN")
                if success!=0:
                        break
        for x in range(3):
                success = nodeAccess("0000","4000","PLUG","OFF")
                if success!=0:
                        break
##        for x in range(3):
##                success = nodeAccess("7000","CONN","CLOSE")
##                if success!=0:
##                        break

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
		
		print("format into{}:".format(rcvString))
		rcvSplitFrame = rcvString.split("`")
		
		dvaddress = rcvSplitFrame[0]
		address = rcvSplitFrame[1]
		command = rcvSplitFrame[2]
		data = rcvSplitFrame[3]
		msg_time = datetime.datetime.now()
		
		if(command == "ALERT"):
                        alertProcess()
##			if((msg_time.year>alert_time.year) | (msg_time.month>alert_time.month) | (msg_time.day>=alert_time.day)):
##                                if((msg_time.hour==alert_time.hour) & (msg_time.minute>alert_time.minute+3 )):
##                                        alert_time = msg_time
##                                	alertProcess()
##			
##                        elif(msg_time.hour>alert_time.hour):
##                                alert_time = msg_time
##                                alertProcess()
		

		if(command == "ID"):
                        logFlag = functions.logSignIn(data)#yollanan mesajin 
                        print "logFlag:",logFlag
                        if logFlag == 1:
                                radio.stopListening()
                                time.sleep(1/4)
                                radio.write("0000`5000`ID`OK`")
                                print "ID confirmed."
                                
                        elif logFlag == 0: 
                                radio.stopListening()
                                time.sleep(1/4)
                                radio.write("0000`5000`ID`NOT`")
                                print "ID denied!"

                if(command == "WINDOW"):
                        functions.windowState(data,address)
                        radio.stopListening()
                        str_message = "0000`"
                        str_message = str_message + address + "`WINDOW`ACK`"
                        radio.write(str_message)
                        
##############################
	sendmessage = fetchCommand()

	if not sendmessage == "":
                splitFrame = sendmessage.split("`")
                dvaddress = splitFrame[0]
		address = splitFrame[1]
		command = splitFrame[2]
		data = splitFrame[3]
				
		if(address=="0000"):	#address of raspberry pi
			if(command=="CAPTURE"):#requested duty
				functions.take_photo(photo_counter)
				photo_counter+=1
				print("photo counter = ",photo_counter)
				if photo_counter>=6:
					photo_counter = 1

				functions.setFlagZero()

				
			
		else:
                        accessFlag = 0
                        for x in range(3):
                                messageFrame = nodeAccess(dvaddress,address,command,data)
                                if messageFrame != 0:
                                        accessFlag = 1
                                        break
                        if accessFlag == 0:
                                functions.setFlagZero()
                        if accessFlag == 1:
                                dvaddress = messageFrame[0]
                                address = messageFrame[1]
                                command = messageFrame[2]
                                data = messageFrame[3]
                        
                                if command=="LIGHT":
                                        if data =="ACK":
                                                print "light turned on succesfully"
                                                functions.dbStateToggle(dvaddress) #toggles state variable in db for given address
                                                functions.setFlagZero()
                                                data = ""

                                        if data == "NACK":
                                                print "Attempt failed!"
                                                data = ""

                                if command=="PLUG":
                                        if data == "ACK":
                                                print "plug diactivated succesfully"
                                                functions.dbStateToggle(dvaddress)
                                                functions.setFlagZero()
                                                data = ""
                                        if data == "NACK":
                                                print "Attempt failed!"
                                                data == ""
                                                
                                if command == "VALVE":
                                        if data == "ACK":
                                                print "operation succesful"
                                                functions.dbStateToggle(dvaddress)
                                                functions.setFlagZero()
                                                data = ""
                                        if data == "NACK":
                                                print "Attempt failed!"
                                                data = ""

                                if command == "CAPTURE":
                                        if data == "ACK":
                                                print "operation succesful"
                                                functions.setFlagZero()
                                                data = ""
                                        if data == "NACK": 
                                                print "Attempt failed!"
                                                data = ""
                                accessFlag = 0


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
##		functions.sec_photo()
		getTemp("")		
		if now_min<55:
			then_min = now_min + 5
		else:
			then_min = now_min - 55
			if now_hour ==23:
				then_hour = 0
			else:
				then_hour = now_hour + 1


