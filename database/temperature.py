#!/usr/bin/env python

import MySQLdb

ldb = MySQLdb.connect("localhost","monitor","password","pass")
lcurs = ldb.cursor()

lcurs.execute("SELECT * FROM pws")

for reading in lcurs.fetchall():
	host=str(reading[1])
	user=str(reading[2])
	pw=str(reading[3])

ldb.rollback()

db = MySQLdb.connect(host,user,pw,user)
cur=db.cursor()

try:
	cur.execute("INSERT INTO temps values(CURRENT_DATE() - INTERVAL 1 DAY, NOW(), 'kitchen', 21.7)")
	cur.execute("INSERT INTO temps values(CURRENT_DATE(),NOW()-interval 12 hour, 'kitchen', 20.6)")
	cur.execute("INSERT INTO temps values(CURRENT_DATE(),NOW(),'kitchen', 22.9)")
	db.commit()
	print "Data committed"
except:
	print"Error: database is being rolled back"
	db.rollback()
