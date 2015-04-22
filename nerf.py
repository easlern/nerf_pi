# RPi->nrf24l01+/pic18lf2525 interface

# RPi is always the master.
# An OVER AND OUT is necessary after every command (well not strictly 
#   necessary if RPi is the last to send a byte, but why be 
#   inconsistent?) so the PIC has time to clear MISO (the line 
#   RPi checks as a "send me a command!" flag.)
# Set target for my messages:
#	RPi -> 0x01,0x02,0x03,0x04,0x05 	#Address 1.2.3.4.5
#	RPi -> 0x00				#OVER AND OUT
# Send a message:
#	RPi -> 0x01 				#I'm sending a message. . .
#	RPi -> 0x03 				#three bytes long
#	RPi -> 0x69,0x69,0x69			#here's the message!
#	RPi -> 0x00				#OVER AND OUT
# Receive message (when no messages are available):
#	RPi -> 0x03				#Got something for me?
#	RPi <- 0x00				#Nope! Go away.
#	RPi -> 0x00				#OVER AND OUT
# Receive message (when one or more messages are available):
#	RPi -> 0x03				#Got something for me?
#	RPi <- 0x01				#Yup!
#	RPi <- 0x02				#two bytes long
#	RPi <- 0x69,0x33			#here's the message!
#	RPi -> 0x00				#OVER AND OUT
# Nil (needs to be sent if the "send me a command!" flag is set, 
#   so the PIC can go back to doing whatever it is the PIC does.)
#	RPi -> 0x00				#OVER AND OUT

import bitbang


OVER_AND_OUT		= 0x00
SEND_A_MESSAGE 		= 0x01
SET_TARGET_ADDRESS 	= 0x02
RECEIVE_A_MESSAGE	= 0x03

class Message:
	def __init__ (self, toAddressBytes, payloadBytes):
		self.toAddressBytes = toAddressBytes
		self.payloadBytes = payloadBytes
	def toComparable (self):
		comparable = (self.toAddressBytes, self.payloadBytes)
		return comparable
	def equals (self, other):
		if (type (self) != type (other)):
			return False
		okay = True
		okay &= self.toAddressBytes == other.toAddressBytes
		okay &= self.payloadBytes == other.payloadBytes
		return okay

class Nerf:
	def __init__ (self, addressBytes, clockPin, misoPin, mosiPin, enablePin, bitBanger = None):
		self.addressBytes = addressBytes
		if (bitBanger == None):
			bitBanger = bitbang.BitBanger (clockPin, misoPin, mosiPin, enablePin)
		self.bitBanger = bitBanger
		# wait a bit for the PIC to cycle up
		for x in range (1000000):
			pass
	def __sendCommand__ (self, command):
		self.bitBanger.sendByte (command)
	def __sendCommandWithFixedLengthPayload__ (self, command, payload):
		if (type (payload) != type ([])):
			raise 'Error in sendCommandWithFixedLengthPayload(): need a list, not a ' + type (bytes) + '!'
		self.__sendCommand__ (command)
		for byte in payload:
			self.bitBanger.sendByte (byte)
	def __sendCommandWithVariableLengthPayload__ (self, command, payload):
		if (type (payload) != type ([])):
			raise 'Error in sendCommandWithVariableLengthPayload(): need a list, not a ' + type (bytes) + '!'
		self.__sendCommand__ (command)
		self.bitBanger.sendByte (len (payload))
		for byte in payload:
			self.bitBanger.sendByte (byte)
	def __receiveFixedLengthPayload__ (self, byteCount):
		bytes = list()
		for x in range (byteCount):
			bytes.append (self.bitBanger.receiveByte())
		return bytes
	def __receiveVariableLengthPayload__ (self):
		length = self.bitBanger.receiveByte()
		return self.__receiveFixedLengthPayload__ (length)
	def sendMessage (self, toAddressBytes, payloadBytes):
		#print ('sending message')
		self.__sendCommandWithFixedLengthPayload__ (SET_TARGET_ADDRESS, toAddressBytes)
		self.__sendCommand__ (OVER_AND_OUT)
		self.__sendCommandWithVariableLengthPayload__ (SEND_A_MESSAGE, payloadBytes)
		self.__sendCommand__ (OVER_AND_OUT)
		#print ('done sending message')
	def receiveMessage (self):
		#print ('receiving message')
		self.__sendCommand__ (RECEIVE_A_MESSAGE)
		bytes = self.__receiveVariableLengthPayload__()
		if (len (bytes) < 1):
			#print ('no message waiting')
			self.__sendCommand__ (OVER_AND_OUT)
			return None
		#print ('message of ' + str(len (bytes)) + ' bytes waiting!')
		message = Message (self.addressBytes, bytes)
		self.__sendCommand__ (OVER_AND_OUT)
		#print ('received message ' + str (len (message.payloadBytes)) + ' bytes long: ' + str (message.payloadBytes))
		return message
