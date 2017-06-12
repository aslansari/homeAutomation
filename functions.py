import os
import datetime
import MySQLdb
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s:%(message)s')

file_handler = logging.FileHandler('main_program_error.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def take_photo(photo_counter):
	logger.info("Taking a photo...")
	os.system('fswebcam -r 640x360 buffer.jpg')
	
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
	logger.info("Taking a photo...")

	os.system('fswebcam -r 640x360 buffer2.jpg')

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

def setFlagZero():
	db = MySQLdb.connect("localhost","monitor","password","commands")
	cur = db.cursor()

	try:
		cur.execute("update module SET flag=0 where flag=1")
		cur.execute("update cmd SET flag=0 where flag=1")
		cur.execute("update data SET flag=0 where flag=1")
		cur.execute("update cmdready SET flag=0 where flag=1")
		db.commit()
		logger.debug("Flags resetted.")
	except:
		db.rollback()
		logger.error("Flag reset failed!")

def logSignIn(self):
        db = MySQLdb.connect("localhost","monitor","password","logs")
        cur = db.cursor()
        cur.execute("select * from signid")
        for signId in cur.fetchall():
                if signId[1] == self:
                        signinName = signId[0] 
                        strdb = "insert into signin values"
                        strdb = strdb + "(\'" + signinName + "\'" + ",current_date(),now())"
                        try:
                                cur.execute(strdb)
                                db.commit()
                                logger.debug("commited logs")
                        except:
                                db.rollback()
                                logger.error("database rolled back, couldn't log signin data")

                        return 1
        return 0 #unregistered user


def windowState(wState,node):
        db = MySQLdb.connect("localhost","monitor","password","commands")
        cur = db.cursor()
        if wState == "OPEN":
                strdb = "update status SET state=1 where node="
                strdb = strdb + "'" + node + "'"
                cur.execute(strdb)
                db.commit()
        elif wState == "CLOSE":
                strdb = "update status SET state=0 where node="
                strdb = strdb + "'" + node + "'"
                cur.execute(strdb)
                db.commit()

def dbStateToggle(node):
        db = MySQLdb.connect("localhost","monitor","password","commands")
        cur = db.cursor()
        strdb = "select state from status where node="
        strdb = strdb + "'" + node + "'"
        cur.execute(strdb)
        state = cur.fetchone()
        try:
                if state[0] == 1:
                        strdb = "update status SET state=0 where node="
                        strdb = strdb + "'" + node + "'"
                        cur.execute(strdb)
                        db.commit()
                elif state[0] == 0:
                        strdb = "update status SET state=1 where node="
                        strdb = strdb + "'" + node + "'"
                        cur.execute(strdb)
                        db.commit()
        except TypeError:
                logger.exception("TypeError")








                
