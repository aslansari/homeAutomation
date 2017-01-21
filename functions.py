import os
import datetime
import MySQLdb


def take_photo(photo_counter):
	print("Taking a photo...")
	os.system('fswebcam -r 1280x720 buffer.jpg')
	
	if photo_counter==1:
		os.system('sudo cp buffer.jpg /var/www/html/kamera/buffer1.jpg')
	elif photo_counter==2:
		os.system('sudo cp buffer.jpg /var/www/html/kamera/buffer2.jpg')
	elif photo_counter==3:
		os.system('sudo cp buffer.jpg /var/www/html/kamera/buffer3.jpg')
	elif photo_counter==4:
		os.system('sudo cp buffer.jpg /var/www/html/kamera/buffer4.jpg')
	elif photo_counter==5:
		os.system('sudo cp buffer.jpg /var/www/html/kamera/buffer5.jpg')
	

def sec_photo():
	print "Taking a photo..."

	os.system('fswebcam -r 1280x720 buffer2.jpg')

	now = datetime.datetime.now()
	
	str_now = str(now.isoformat())
	
	str_system = "cp buffer2.jpg ~/camera/"
	str_system = str_system + str_now 
	str_system = str_system + ".jpg"
	
	os.system(str_system)

	photo_db = MySQLdb.connect("localhost","monitor","password","temps")
	curs = photo_db.cursor()
	
	str_db = "insert into photo (time) values"
	str_db = str_db + "(" + "\'" + str_now + "\'" + ")"
	
	curs.execute(str_db)
	photo_db.commit()
