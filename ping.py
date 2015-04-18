from nerf import *


# Address bytes, pins
#nerfer = Nerf (5, 3,5,7,8)
nerfer = Nerf (5, 19,21,23,24) # Try not using I2C pins (they automatically pull-up I guess?)

while (True):
	nerfer.sendMessage ([2,2,2,2,2], [0x48, 0x45, 0x4c, 0x4c, 0x4f, 0x20, 0x59, 0x4f])
	message = nerfer.receiveMessage()
	break
