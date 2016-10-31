import MySQLdb

ldb = MySQLdb.connect("localhost","monitor","password","pass")
curs= ldb.cursor()

curs.execute("SELECT * FROM pws")

for reading in curs.fetchall():
        host=str(reading[1])
	user=str(reading[2])
        pw=str(reading[3])
ldb.rollback()
        
db = MySQLdb.connect(host,user,pw,user)
cur=db.cursor()

cur.execute("SELECT * FROM temps")

print "\nDate		Time		Zone		Temperature"
print "============================================================"

for reading in cur.fetchall():
	print str(reading[0])+"	"+str(reading[1])+"  	"+\
		str(reading[2])+"		"+str(reading[3])

