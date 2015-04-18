import unittest
import bitbang
import nerf


CLK_PIN 	= 1
MISO_PIN 	= 3
MOSI_PIN	= 5
ENABLE_PIN	= 8

PUD_DOWN	= 0
PUD_UP		= 1


class BbTester:
	def __init__ (self):
		self.BOARD = 'BOARD'
		self.OUT = 'OUT'
		self.IN = 'IN'
		self.HIGH = True
		self.LOW = False
		self.pinModes = dict()
		self.pinActions = []
		self.pinSettings = dict()
		self.PUD_DOWN = PUD_DOWN
		self.PUD_UP = PUD_UP
	def setup (self, pin, mode, pull_up_down=PUD_DOWN):
		self.pinModes [pin] = mode
		self.pinSettings [MISO_PIN] = [self.HIGH]
	def setmode (self, mode):
		self.mode = mode
	def input (self, pin):
		if pin in self.pinSettings and len (self.pinSettings [pin]) > 0:
			setting = self.pinSettings [pin][0]
			if len (self.pinSettings [pin]) > 1:
				del self.pinSettings [pin][0]
			return setting
		return self.LOW
	def output (self, pin, newState):
		self.pinSettings [pin] = [newState]
		self.pinActions.append ((pin, newState))

class BbMock:
	def __init__ (self):
		self.bytesFromMaster = list()
		self.bytesToMaster = list()
	def sendByte (self, byte):
		self.bytesFromMaster.append (byte)
	def receiveByte (self):
		byte = self.bytesToMaster [0]
		del self.bytesToMaster [0]
		return byte

class BitBangerTests (unittest.TestCase):
	def setUp (self):
		pass
	def test_setup (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		self.assertEqual (tester.BOARD, tester.mode)
		self.assertEqual (tester.OUT, tester.pinModes [CLK_PIN])
		self.assertEqual (tester.IN, tester.pinModes [MISO_PIN])
		self.assertEqual (tester.OUT, tester.pinModes [MOSI_PIN])
		self.assertEqual (tester.OUT, tester.pinModes [ENABLE_PIN])
	def test_set (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		banger.set (CLK_PIN)
		banger.clear (CLK_PIN)
		self.assertEqual ([(ENABLE_PIN,tester.LOW),(ENABLE_PIN,tester.HIGH),(CLK_PIN,tester.HIGH),(CLK_PIN,tester.LOW)], tester.pinActions)
	def test_clear (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		banger.clear (CLK_PIN)
		banger.set (CLK_PIN)
		self.assertEqual ([(ENABLE_PIN,tester.LOW),(ENABLE_PIN,tester.HIGH),(CLK_PIN,tester.LOW),(CLK_PIN,tester.HIGH)], tester.pinActions)
	def test_setClock (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		banger.setClock()
		self.assertEqual ([(ENABLE_PIN,tester.LOW),(ENABLE_PIN,tester.HIGH),(CLK_PIN,tester.HIGH)], tester.pinActions)
	def test_clearClock (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		banger.clearClock()
		self.assertEqual ([(ENABLE_PIN,tester.LOW),(ENABLE_PIN,tester.HIGH),(CLK_PIN,tester.LOW)], tester.pinActions)
	def test_getMiso (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		tester.pinSettings [MISO_PIN] = [tester.HIGH]
		self.assertEqual (tester.HIGH, banger.getMiso())
	def test_setMosi (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		banger.setMosi()
		self.assertEqual ([(ENABLE_PIN,tester.LOW),(ENABLE_PIN,tester.HIGH),(MOSI_PIN,tester.HIGH)], tester.pinActions)
	def test_clearMosi (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		banger.clearMosi()
		self.assertEqual ([(ENABLE_PIN,tester.LOW),(ENABLE_PIN,tester.HIGH),(MOSI_PIN,tester.LOW)], tester.pinActions)
	def test_receiveByte (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		tester.pinSettings [MISO_PIN] = [tester.LOW, tester.HIGH, tester.LOW, tester.HIGH, tester.LOW, tester.HIGH, tester.LOW, tester.HIGH]
		result = banger.receiveByte()
		self.assertEqual (0x55, result)
	def test_sendByte (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		banger.sendByte (0x55)
		c = CLK_PIN
		m = MOSI_PIN
		e = ENABLE_PIN
		h = tester.HIGH
		l = tester.LOW
		self.assertEqual ([(e,l),(e,h),(c,l),(m,l),(c,h),(c,l),(m,h),(c,h),(c,l),(m,l),(c,h),(c,l),(m,h),(c,h),(c,l),(m,l),(c,h),(c,l),(m,h),(c,h),(c,l),(m,l),(c,h),(c,l),(m,h),(c,h),(c,l)], tester.pinActions)
	def test_sendByteLastBit (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		banger.sendByte (0x01)
		c = CLK_PIN
		m = MOSI_PIN
		e = ENABLE_PIN
		h = tester.HIGH
		l = tester.LOW
		self.assertEqual ([(e,l),(e,h),(c,l),(m,l),(c,h),(c,l),(m,l),(c,h),(c,l),(m,l),(c,h),(c,l),(m,l),(c,h),(c,l),(m,l),(c,h),(c,l),(m,l),(c,h),(c,l),(m,l),(c,h),(c,l),(m,h),(c,h),(c,l)], tester.pinActions)
	def test_waitForReadySignal (self):
		tester = BbTester()
		banger = bitbang.BitBanger (CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, tester)
		tester.pinSettings [MISO_PIN] = [tester.LOW]
		with self.assertRaises (bitbang.SendByteTimeoutException):
			banger.sendByte (0x00)
		tester.pinSettings [MISO_PIN] = [tester.HIGH]
		banger.sendByte (0x00)

class NerfTests (unittest.TestCase):
	def setUp (self):
		pass
	def test_sendMessage_length1 (self):
		bbMock = BbMock ()
		nrf = nerf.Nerf ([1,2,3,4,5], CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, bbMock)
		nrf.sendMessage ([5,4,3,2,1], [0x55])
		self.assertEqual ([0x02,5,4,3,2,1,0x01,1,0x55,0], bbMock.bytesFromMaster)
	def test_sendMessage_length2 (self):
		bbMock = BbMock ()
		nrf = nerf.Nerf ([1,2,3,4,5], CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, bbMock)
		nrf.sendMessage ([5,4,3,2,1], [0x55, 0x69])
		self.assertEqual ([0x02,5,4,3,2,1,0x01,2,0x55,0x69,0], bbMock.bytesFromMaster)
	def test_receiveMessage_noneWaiting (self):
		bbMock = BbMock ()
		nrf = nerf.Nerf ([1,2,3,4,5], CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, bbMock)
		bbMock.bytesToMaster = [0x00]
		received = nrf.receiveMessage()
		self.assertEquals (None, received)
		self.assertEquals ([0x04,0], bbMock.bytesFromMaster)
	def test_receiveMessage_length1 (self):
		bbMock = BbMock ()
		nrf = nerf.Nerf ([1,2,3,4,5], CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, bbMock)
		bbMock.bytesToMaster = [0x01,1,0x99]
		received = nrf.receiveMessage()
		self.assertEquals (([1,2,3,4,5],[0x99]), received.toComparable())
		self.assertEquals ([0x04,0x03,0], bbMock.bytesFromMaster)
	def test_receiveMessage_length2 (self):
		bbMock = BbMock ()
		nrf = nerf.Nerf ([1,2,3,4,5], CLK_PIN, MISO_PIN, MOSI_PIN, ENABLE_PIN, bbMock)
		bbMock.bytesToMaster = [1,2,0x99,0x11]
		received = nrf.receiveMessage()
		self.assertEquals (([1,2,3,4,5],[0x99,0x11]), received.toComparable())
		self.assertEquals ([0x04,0x03,0], bbMock.bytesFromMaster)


if (__name__ == '__main__'):
    unittest.main()
