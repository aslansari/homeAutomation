import smtplib
import functions

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def sendMail():
	try:
	       fp = open("alertMail.txt", 'rb')
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
	print "photo has taken"
	
	try:
		imagefile = open("buffer2.jpg",'rb')
		img = MIMEImage(imagefile.read())
	finally:
		imagefile.close()
	print "attach image to mail"
	msg.attach(img)
	print "attach body to mail"
	msg.attach(body)	
		
	username ='sydyotomasyon@gmail.com'
	password = '@bccastle2'
	print "logging in smtp server"	
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.ehlo()
	server.starttls()
	server.login(username, password)
	print "sending mail"
	try:
		server.sendmail(fromaddr, toaddrs, msg.as_string())
		print "Succesfully sent the email"
	except:
		print "unable to send email"
	server.quit()

