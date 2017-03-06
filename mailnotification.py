import smtplib
import functions

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def sendMail():
	try:
	       fp = open("textfile.txt", 'rb')
	       body = MIMEText(fp.read())
	finally:
	        fp.close()
	
	msg = MIMEMultipart()
	fromaddr = 'sydyotomasyon@gmail.com'
	toaddrs  = 'aslan.sari022@gmail.com'
	msg['Subject'] = "Dikkat!!!"
	msg['From'] = fromaddr
	msg['To'] = toaddrs
	msg.preamble = "Sicaklik sensoru!!!\n"
	
	functions.sec_photo()
	
	try:
		imagefile = open("buffer2.jpg",'rb')
		img = MIMEImage(imagefile.read())
	finally:
		imagefile.close()
	
	msg.attach(img)
	msg.attach(body)	
		
	username ='sydyotomasyon@gmail.com'
	password = '@bccastle2'
	
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.ehlo()
	server.starttls()
	server.login(username, password)
	server.sendmail(fromaddr, toaddrs, msg.as_string())
	server.quit()

