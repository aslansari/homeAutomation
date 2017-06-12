import os
import datetime
import MySQLdb


def take_photo(photo_counter):
	print("Taking a photo...")
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
	print "Taking a photo..."

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
		print "Flags resetted."
	except:
		db.rollback()
		print "Flag reset failed!"

def logSignIn(self):
        db = MySQLdb.connect("localhost","monitor","password","logs")
        cur = db.cursor()
        print self
        cur.execute("select * from signid")
        for signId in cur.fetchall():
                if signId[1] == self:
                        signinName = signId[0] 
                        strdb = "insert into signin values"
                        strdb = strdb + "(\'" + signinName + "\'" + ",current_date(),now())"
                        try:
                                cur.execute(strdb)
                                db.commit()
                                print "commited logs"
                        except:
                                db.rollback()

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
                print "TypeError"








                
