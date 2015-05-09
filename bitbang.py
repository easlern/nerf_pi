import RPi.GPIO as GPIO
import time
import sys


LOOPS_IN_WAIT = 50

class SendByteTimeoutException (Exception):
	def __init__ (self):
		Exception.__init__ (self)

class BitBanger:
	def __init__ (self, clockPin, misoPin, mosiPin, enablePin, gpio = GPIO):
		self.gpio = gpio
		self.clockPin = clockPin
		self.misoPin = misoPin
		self.mosiPin = mosiPin
		self.enablePin = enablePin
		self.gpio.setmode (gpio.BOARD)
		self.gpio.setup (self.clockPin, gpio.OUT)
		self.gpio.setup (self.misoPin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
		#print ("using misoPin " + str(self.misoPin))
		self.gpio.setup (self.mosiPin, gpio.OUT)
		self.gpio.setup (self.enablePin, gpio.OUT)
		# Disable to start
		self.clear (self.enablePin)
		# Wait a bit for things to disable
		for x in range (1000000):
			pass
		# Enable now
		self.set (self.enablePin)
		# Wait a bit for things to start up
		for x in range (1000000):
			pass
	def __del__ (self):
		#print ('cleaning up')
		self.clear (self.enablePin)
		self.gpio.cleanup()
		#print ('cleaned up')
	def set (self, pin):
		self.gpio.output (pin, self.gpio.HIGH)
	def clear (self, pin):
		self.gpio.output (pin, self.gpio.LOW)
	def get (self, pin):
		return self.gpio.input (pin) == 1 #self.gpio.HIGH
	def setClock (self):
		self.set (self.clockPin)
	def clearClock (self):
		self.clear (self.clockPin)
	def getMiso (self):
		return self.get (self.misoPin)
	def setMosi (self):
		self.set (self.mosiPin)
	def clearMosi (self):
		self.clear (self.mosiPin)
	def wait (self):
		for x in range (LOOPS_IN_WAIT):
			pass
	def receiveByte (self):
		# We are always master!
		received = 0x00
		self.clearClock()
		self.wait()
		for nextBit in range (7, -1, -1):
			self.setClock()
			self.wait()
			if (self.getMiso()):
				received |= 0x01 << nextBit
			self.clearClock()
			self.wait()
		return received
	def sendByte (self, byte):
		try:
			#print ("sending byte " + str (byte))
			# Wait for the PIC to signal it's ready for 
			#   a byte.
			startedWaiting = time.time()
			while not self.getMiso():
				if time.time() - startedWaiting > .5:
					raise SendByteTimeoutException()
			# We are always master!
			for nextBit in range (7, -1, -1):
				self.clearClock()
				self.wait()
				if (byte & (0x01 << nextBit)):
					self.setMosi()
				else:
					self.clearMosi()
				self.setClock()
				self.wait()
			self.clearClock()
		except SendByteTimeoutException:
			print ("sending byte timed out!")
			raise Exception()
