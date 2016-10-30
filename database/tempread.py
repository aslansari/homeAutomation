import MySQLdb

db = MySQLdb.connect("sql7.freesqldatabase.com","sql7142358","64Uw2DMVcT","sql7142358")
cur=db.cursor()

cur.execute("SELECT * FROM temps")

print "\nDate		Time		Zone		Temperature"
print "============================================================"

for reading in cur.fetchall():
	print str(reading[0])+"	"+str(reading[1])+"	"+\
		str(reading[2])+"		"+str(reading[3])

