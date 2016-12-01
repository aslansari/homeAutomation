import os

os.system('fswebcam -r 1280x720 buffer.jpg')
os.system('sudo cp buffer.jpg /var/www/html/kamera/buffer1.jpg')
