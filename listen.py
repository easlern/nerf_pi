from nerf import *
import time
import sys
import os.path
import os

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0) # Set output unbuffered


# Address bytes, pins
#nerfer = Nerf (5, 3,5,7,8)
nerfer = Nerf (5, 19,21,23,24) # Try not using I2C pins (they automatically pull-up I guess?)

lease = 0
if (len (sys.argv) > 1):
	lease = int (sys.argv[1])
while (lease > 0 or not os.path.exists ('stopListening.flag')):
	lease -= 1
	for x in range (100):
		#nerfer.sendMessage ([2,2,2,2,2], [0x48, 0x45, 0x4c, 0x4c, 0x4f, 0x20, 0x59, 0x4f])
		message = None
		message = nerfer.receiveMessage()
		if (message is not None):
			messageAsString = "".join(map(chr, message.payloadBytes))
			print (messageAsString)
