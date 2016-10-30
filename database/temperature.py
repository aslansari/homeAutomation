#!/usr/bin/env python

import MySQLdb

db = MySQLdb.connect("sql7.freesqldatabase.com","sql7142358","64Uw2DMVcT","sql7142358")
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
