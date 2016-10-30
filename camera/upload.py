import ftplib
import os

myftp = ftplib.FTP()

host = "deccoyi.bplaced.net"
port = 21
myftp.connect(host,port)

try:
	print("Logging in...")
	myftp.login("deccoyi_rp","yabanmersini")
	print("Logged in.")
except:
	print("login failed.")

os.system("python shot.py")

file = open('buffer.jpg','rb')
myftp.storbinary('STOR buffer.jpg', file)

print("logging off..")

myftp.close()
print("connection ended.")
