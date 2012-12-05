#!/usr/bin/python -u
'''PowerMeter Data Processor for Brultech ECM-1240.

Thanks to:
	Amit Snyderman <amit@amitsnyderman.com>
	bpwwer & tenholde from the cocoontech.com forums
	Kelvin Kakugawa
	brian jackson [http://fivejacksons.com/brian/]
	Marc MERLIN <marc_soft@merlins.org> | http://marc.merlins.org/perso/solar/

Changelog:
- 0.1.4. 2010/06/06: modified screen output code to 
* Show Kwh counters for each input as well as instant W values
* For channel 1 & 2, show positive and negative values.

Example output:
2010/06/07 21:48:37: Volts:                 120.90V
2010/06/07 21:48:37: Ch1 Watts:            -124.586KWh ( 1536W) < PG&E
2010/06/07 21:48:37: Ch1 Positive Watts:    210.859KWh ( 1536W)
2010/06/07 21:48:37: Ch1 Negative Watts:    335.445KWh (    0W)
2010/06/07 21:48:37: Ch2 Watts:            -503.171KWh (    0W) < PV
2010/06/07 21:48:37: Ch2 Positive Watts:      0.028KWh (    0W)
2010/06/07 21:48:37: Ch2 Negative Watts:    503.199KWh (    0W)
2010/06/07 21:48:37: Aux1 Watts:            114.854KWh (  311W) < Computer Closet
2010/06/07 21:48:37: Aux2 Watts:             80.328KWh (  523W) < MythTV/AV System
2010/06/07 21:48:37: Aux3 Watts:             13.014KWh (   35W) < Computer Office/BR4
2010/06/07 21:48:37: Aux4 Watts:              4.850KWh (    0W) < AC
2010/06/07 21:48:37: Aux5 Watts:             25.523KWh (  137W) < Kitchen Fridge


'''
__author__	= 'Brian Jackson; Kelvin Kakugawa; Marc MERLIN'
__version__	= '0.1.4'

import base64
import bisect
import new
import optparse
import socket
import sys
import time
import traceback
import urllib
import urllib2

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning) # MySQLdb in 2.6.*

# External (Optional) Dependencies
try:
	import serial
except Exception, e:
	serial = None

try:
	import MySQLdb
except Exception, e:
	MySQLdb = None

try:
	import cjson as json

	# XXX: maintain compatibility w/ json module
	setattr(json, 'dumps', json.encode)
	setattr(json, 'loads', json.decode)

except Exception, e:
	try:
		import simplejson as json
	except Exception, e:
		import json


MINUTE	= 60
HOUR	= 60 * MINUTE
DAY		= 24 * HOUR

# PACKET SETTINGS
START_HEADER0	= hex(254)
START_HEADER1	= hex(255)
START_HEADER2	= hex(3)

DATA_BYTES_LENGTH = 62
SEC_COUNTER_MAX   = 16777216

# SERIAL SETTINGS
SERIALPORT	= "/dev/ttyUSB0"	# the com/serial port the ecm is connected to (COM4, /dev/ttyS01, etc)
BAUDRATE	= 19200				# the baud rate we talk to the ecm

# ETHERNET SETTINGS
HOST = ''
PORT = 8083		# default port that the EtherBee is pushing data to

# DATABASE DEFAULTS
DB_HOST		= 'localhost'
DB_USER		= ''
DB_PASSWD	= ''
DB_DATABASE	= ''

# WATTZON DEFAULTS
WATTZON_API_URL = 'http://www.wattzon.com/api/2009-01-27/3'


# Helper Functions

def calculate(now, prev):
	'''calc average watts/s between packets'''
	if now['secs'] < prev['secs']:
		now['secs'] += SEC_COUNTER_MAX # handle seconds counter overflow
	secs_delta = float(now['secs'] - prev['secs'])

	# CH1/2 Watts
	now['ch1_watts'] = (now['ch1_aws'] - prev['ch1_aws']) / secs_delta
	now['ch2_watts'] = (now['ch2_aws'] - prev['ch2_aws']) / secs_delta

	now['ch1_positive_watts'] = (now['ch1_pws'] - prev['ch1_pws']) / secs_delta
	now['ch2_positive_watts'] = (now['ch2_pws'] - prev['ch2_pws']) / secs_delta

	now['ch1_negative_watts'] = now['ch1_watts'] - now['ch1_positive_watts']
	now['ch2_negative_watts'] = now['ch2_watts'] - now['ch2_positive_watts']

	# All Watts increase no matter which way the current is going
	# Polar Watts only increase if the current is positive
	# Every Polar Watt does register as an All Watt too.
	# math comes to: Watts = 2x Polar Watts - All Watts
	now['ch1_pwh']  = now['ch1_pws'] / 3600000.0
	now['ch2_pwh']  = now['ch2_pws'] / 3600000.0
	now['ch1_nwh']  = (now['ch1_aws'] - now['ch1_pws']) / 3600000.0
	now['ch2_nwh']  = (now['ch2_aws'] - now['ch2_pws']) / 3600000.0
	now['ch1_wh']   = now['ch1_pwh'] - now['ch1_nwh']
	now['ch2_wh']   = now['ch2_pwh'] - now['ch2_nwh']


	now['aux1_wh'] = now['aux1_ws'] / 3600000.0
	now['aux2_wh'] = now['aux2_ws'] / 3600000.0
	now['aux3_wh'] = now['aux3_ws'] / 3600000.0
	now['aux4_wh'] = now['aux4_ws'] / 3600000.0
	now['aux5_wh'] = now['aux5_ws'] / 3600000.0


        # Polar Watts' instant value's only purpose seems to help find out if
        # main watts are positive or negative. Polar Watts only goes up if the
        # sign is positive. If they are null, tha means the sign is negative.
	if (now['ch1_positive_watts'] == 0):
		now['ch1_watts'] *= -1 
	if (now['ch2_positive_watts'] == 0):
		now['ch2_watts'] *= -1 

	# AUX1-5 Watts
	now['aux1_watts'] = (now['aux1_ws'] - prev['aux1_ws']) / secs_delta
	now['aux2_watts'] = (now['aux2_ws'] - prev['aux2_ws']) / secs_delta
	now['aux3_watts'] = (now['aux3_ws'] - prev['aux3_ws']) / secs_delta
	now['aux4_watts'] = (now['aux4_ws'] - prev['aux4_ws']) / secs_delta
	now['aux5_watts'] = (now['aux5_ws'] - prev['aux5_ws']) / secs_delta

	now['time'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())


# Packet Server Classes

class BasePacketServer(object):
	def __init__(self, packet_processor):
		self.packet_processor = packet_processor

	def _convert(self, bytes):
		return reduce(lambda x,y:x+y[0] * (256**y[1]), zip(bytes,xrange(len(bytes))),0)

	def _compile(self, packet):
		now = {}

		# Voltage Data (2 bytes)
		now['volts'] = 0.1 * self._convert(packet[1::-1])

		# CH1-2 Absolute Watt-Second Counter (5 bytes each)
		now['ch1_aws'] = self._convert(packet[2:7])
		now['ch2_aws'] = self._convert(packet[7:12])

		# CH1-2 Polarized Watt-Second Counter (5 bytes each)
		now['ch1_pws'] = self._convert(packet[12:17])
		now['ch2_pws'] = self._convert(packet[17:22])

		# Reserved (4 bytes)

		# Device Serial Number (2 bytes)
		now['ser_no'] = self._convert(packet[27:25:-1])

		# Reset and Polarity Information (1 byte)
		now['flag'] = self._convert(packet[28:29])

		# Device Information (1 byte)
		now['unit_id'] = self._convert(packet[29:30])

		# CH1-2 Current (2 bytes each)
		now['ch1_amps'] = 0.01 * self._convert(packet[30:32])
		now['ch2_amps'] = 0.01 * self._convert(packet[32:34])

		# Seconds (3 bytes)
		now['secs'] = self._convert(packet[34:37])

		# AUX1-5 Watt-Second Counter (4 bytes each)
		now['aux1_ws'] = self._convert(packet[37:41])
		now['aux2_ws'] = self._convert(packet[41:45])
		now['aux3_ws'] = self._convert(packet[45:49])
		now['aux4_ws'] = self._convert(packet[49:53])
		now['aux5_ws'] = self._convert(packet[53:57])

		return now

	def process(self, packet):
		packet = self._compile(packet)

		self.packet_processor.preprocess(packet)
		self.packet_processor.process(packet)

	def read(self):
		pass
	
	def run(self):
		try:
			self.packet_processor.setup()

			while True:
				try:
					self.read()

				except Exception, e:
					if type(e) == KeyboardInterrupt: # only break for KeyboardInterrupt
						raise e

					traceback.print_exc()
					if not self.packet_processor.handle(e):
						print 'Exception [in %s]: %s' % (self, e)

		except Exception, e:
			traceback.print_exc()
			sys.exit(1)

		finally:
			self.packet_processor.cleanup()

class SerialPacketServer(BasePacketServer):
	def __init__(self, packet_processor, port=SERIALPORT, baudrate=BAUDRATE):
		super(SerialPacketServer, self).__init__(packet_processor)

		self._port		= port
		self._baudrate	= baudrate

		if not serial:
			print 'Error: pySerial module could not be imported.'
			sys.exit(1)

		self.conn = None

	def read(self):
		try:
			self.conn = serial.Serial(self._port, self._baudrate)
			self.conn.open()

			while True:
				data = self.conn.read(1)
				if not data:
					break

				header_byte0 = hex(ord(data))
				if header_byte0 != START_HEADER0:
					continue

				data = self.conn.read(1)
				header_byte1 = hex(ord(data))
				if header_byte1 != START_HEADER1:
					continue

				data = self.conn.read(1)
				header_byte2 = hex(ord(data))
				if header_byte2 != START_HEADER2:
					continue

				packet = self.conn.read(DATA_BYTES_LENGTH)
				while len(packet) < DATA_BYTES_LENGTH:
					data = self.conn.read(DATA_BYTES_LENGTH-len(packet))
					if not data: # No data left
						raise Exception('Received no data.')
					packet += data
				packet = [ord(c) for c in packet]
				
				self.process(packet)
		
		finally:
			if self.conn:
				self.conn.close()
				self.conn = None

class SocketPacketServer(BasePacketServer):
	def __init__(self, packet_processor, host=HOST, port=PORT):
		super(SocketPacketServer, self).__init__(packet_processor)

		socket.setdefaulttimeout(60) # override None

		self._host = host
		self._port = port

		self.sock = None
		self.conn = None

	def read(self):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			try:
				self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
			except: # REUSEPORT may not be supported on all systems
				pass

			self.sock.bind((self._host, self._port))
			self.sock.listen(1)

			self.conn, addr = self.sock.accept()

			while True:
				data = self.conn.recv(1)
				if not data:
					break
				
				header_byte0 = hex(ord(data))
				if header_byte0 != START_HEADER0:
					continue

				data = self.conn.recv(1)
				header_byte1 = hex(ord(data))
				if header_byte1 != START_HEADER1:
					continue

				data = self.conn.recv(1)
				header_byte2 = hex(ord(data))
				if header_byte2 != START_HEADER2:
					continue

				packet = self.conn.recv(DATA_BYTES_LENGTH)
				while len(packet) < DATA_BYTES_LENGTH:
					data = self.conn.recv(DATA_BYTES_LENGTH-len(packet))
					if not data: # No data left
						raise Exception('Received no data.')
					packet += data
				packet = [ord(c) for c in packet]

				self.process(packet)

		finally:
			if self.conn:
				self.conn.shutdown(socket.SHUT_RD)
				self.conn.close()
				self.conn = None

			if self.sock:
				self.sock.shutdown(socket.SHUT_RD)
				self.sock.close()
				self.sock = None

# Packet Processor Classes

class MovingBuffer(object):
	'''Maintain fixed-size buffer of data over time'''
	def __init__(self, max_timeframe=DAY):
		self.time_points	= []
		self.max_timeframe	= max_timeframe

	def insert(self, timestamp, time_dict):
		bisect.insort(self.time_points, (timestamp, time_dict))

		now = int(time.time())
		cull_index = bisect.bisect(self.time_points, (now-self.max_timeframe, {}))
		del(self.time_points[:cull_index])

	def data_over(self, time_delta):
		now = int(time.time())
		delta_index = bisect.bisect(self.time_points, (now-time_delta, {}))

		return self.time_points[delta_index:]

	def delta_over(self, time_delta):
		now = int(time.time())
		delta_index = bisect.bisect(self.time_points, (now-time_delta, {}))

		offset = self.time_points[delta_index][1]
		current = self.time_points[-1][1]

		calculate(current, offset)
		return current

class BaseProcessor(object):
	def __init__(self, buffer_timeframe, *args, **kwargs):
		self.buffer	= MovingBuffer(buffer_timeframe)

	def setup(self):
		pass

	def preprocess(self, packet):
		self.buffer.insert(int(time.time()), packet)

	def process(self, packet):
		pass
	
	def handle(self, exception):
		return False

	def cleanup(self):
		pass

class PrintMixin(object):
	def __init__(self, *args, **kwargs):
		super(PrintMixin, self).__init__(*args, **kwargs)
		
		self.print_out = kwargs.get('print_out', False)
		self.prev_packet = {}

	def process(self, packet):
		if self.prev_packet:
			calculate(packet, self.prev_packet)

			# start with newline in case previous run was stopped in the middle of a line
			# this ensures that the new Volts line is not attached to some old incompletely
			# written line
			print
			print packet['time']+": Volts:              %9.2fV" % packet['volts']
			print packet['time']+": Ch1 Watts:          % 13.6fKWh (% 5dW)" % (packet['ch1_wh'] , packet['ch1_watts'])
			print packet['time']+": Ch1 Positive Watts: % 13.6fKWh (% 5dW)" % (packet['ch1_pwh'], packet['ch1_positive_watts'])
			print packet['time']+": Ch1 Negative Watts: % 13.6fKWh (% 5dW)" % (packet['ch1_nwh'], packet['ch1_negative_watts'])
			print packet['time']+": Ch2 Watts:          % 13.6fKWh (% 5dW)" % (packet['ch2_wh'] , packet['ch2_watts'])
			print packet['time']+": Ch2 Positive Watts: % 13.6fKWh (% 5dW)" % (packet['ch2_pwh'], packet['ch2_positive_watts'])
			print packet['time']+": Ch2 Negative Watts: % 13.6fKWh (% 5dW)" % (packet['ch2_nwh'], packet['ch2_negative_watts'])
			print packet['time']+": Aux1 Watts:         % 13.6fKWh (% 5dW)" % (packet['aux1_wh'], packet['aux1_watts'])
			print packet['time']+": Aux2 Watts:         % 13.6fKWh (% 5dW)" % (packet['aux2_wh'], packet['aux2_watts'])
			print packet['time']+": Aux3 Watts:         % 13.6fKWh (% 5dW)" % (packet['aux3_wh'], packet['aux3_watts'])
			print packet['time']+": Aux4 Watts:         % 13.6fKWh (% 5dW)" % (packet['aux4_wh'], packet['aux4_watts'])
			print packet['time']+": Aux5 Watts:         % 13.6fKWh (% 5dW)" % (packet['aux5_wh'], packet['aux5_watts'])
		self.prev_packet = packet

		super(PrintMixin, self).process(packet)

class DatabaseMixin(object):
	def __init__(self, *args, **kwargs):
		super(DatabaseMixin, self).__init__(*args, **kwargs)

		self.db_host		= kwargs.get('db_host')		or DB_HOST
		self.db_user		= kwargs.get('db_user')		or DB_USER
		self.db_passwd		= kwargs.get('db_passwd')	or DB_PASSWD
		self.db_database	= kwargs.get('db_database')	or DB_DATABASE
		self.quiet			= kwargs.get('quiet')
	
		if not MySQLdb:
			print 'Error: MySQLdb module could not be imported.'
			sys.exit(1)

	def setup(self):
		super(DatabaseMixin, self).setup()

		try:
			self.conn = MySQLdb.connect(
				host=self.db_host,
				user=self.db_user,
				passwd=self.db_passwd,
				db=self.db_database)
		except Exception, e:
			if type(e) == MySQLdb.Error:
				print 'MySQL Error: [#%d] %s' % (exception.args[0], exception.args[1])
			else:
				traceback.print_exc()

			self.conn = None
			sys.exit(1)

		self.insert_period	= MINUTE
		self.last_insert	= 0

	def process(self, packet):
		super(DatabaseMixin, self).process(packet)
		
		now = int(time.time())
		if not self.last_insert:
			self.last_insert = now
			return
		if now < (self.last_insert+self.insert_period):
			return
		self.last_insert = now

		timestamp = int(time.time())
		try:
			delta = self.buffer.delta_over(self.insert_period)
		except ZeroDivisionError, zde:
			return # not enough data in buffer

		cursor = self.conn.cursor()
		cursor.execute(
'''INSERT INTO '''+self.db_database+'''.ecm (
	ch1_ws,
	ch2_ws,
	aux1_ws,
	aux2_ws,
	aux3_ws,
	aux4_ws,
	aux5_ws,
	time_created
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (
	int(delta['ch1_watts']),
	int(delta['ch2_watts']),
	int(delta['aux1_watts']),
	int(delta['aux2_watts']),
	int(delta['aux3_watts']),
	int(delta['aux4_watts']),
	int(delta['aux5_watts']),
	timestamp))

		if not self.quiet:
			print 'DB: insert @%s w/: ch1: %s, ch2: %s, aux1: %s, aux2: %s, aux3: %s, aux4: %s, aux5: %s' % (
			timestamp,
			delta['ch1_watts'],
			delta['ch2_watts'],
			delta['aux1_watts'],
			delta['aux2_watts'],
			delta['aux3_watts'],
			delta['aux4_watts'],
			delta['aux5_watts'],
			)
		cursor.close()

	def handle(self, exception):
		if type(exception) == MySQLdb.Error:
			print 'MySQL Error: [#%d] %s' % (exception.args[0], exception.args[1])
			return True
		
		return super(DatabaseMixin, self).handle(exception)

	def cleanup(self):
		super(DatabaseMixin, self).cleanup()

		if not self.conn:
			return

		self.conn.commit()
		self.conn.close()

class RequestPostWithContentType(urllib2.Request):
	def __init__(self, content_type, *args, **kwargs):
		urllib2.Request.__init__(self, *args, **kwargs)

		self._content_type = content_type
		urllib2.Request.add_header(self, 'Content-Type', content_type)
	
	def has_header(self, header_name):
		return header_name == 'Content-Type' or urllib2.Request.has_header(self, header_name)

	def get_header(self, header_name, default=None):
		return header_name == 'Content-Type' and self._content_type or \
			urllib2.Request.get_header(self, header_name, default)

class WattzOnMixin(object):
	def __init__(self, *args, **kwargs):
		super(WattzOnMixin, self).__init__(*args, **kwargs)

		self.api_key		= kwargs.get('api_key')
		self.api_username	= kwargs.get('api_username')
		self.api_passwd		= kwargs.get('api_passwd')

		self.meter_ch1	= kwargs.get('meter_ch1')
		self.meter_ch2	= kwargs.get('meter_ch2')
		self.meter_aux1	= kwargs.get('meter_aux1')
		self.meter_aux2	= kwargs.get('meter_aux2')
		self.meter_aux3	= kwargs.get('meter_aux3')
		self.meter_aux4	= kwargs.get('meter_aux4')
		self.meter_aux5	= kwargs.get('meter_aux5')

		self.quiet = kwargs.get('quiet')

	def _create_url(self, meter_name):
		return '%s/user/%s/powermeter/%s/upload.json?key=%s' % (
			WATTZON_API_URL,
			self.api_username,
			urllib.quote(meter_name),
			self.api_key
		)

	def setup(self):
		super(WattzOnMixin, self).setup()

		if not (self.api_key and self.api_username and self.api_passwd and self.meter_ch1):
			print 'WattzOn Error: Insufficient credentials'
			if not self.api_key:
				print '  No API Key'
			if not self.api_username:
				print '  No API Username'
			if not self.api_passwd:
				print '  No API Passord'
			if not self.meter_ch1:
				print '  No Powermeter Name for CH1'
			sys.exit(1)

		p = urllib2.HTTPPasswordMgrWithDefaultRealm()
		p.add_password(
			'WattzOn', WATTZON_API_URL, self.api_username, self.api_passwd)
		auth = urllib2.HTTPBasicAuthHandler(p)
		opener = urllib2.build_opener(auth)
		urllib2.install_opener(opener)

		self.ch1_url = self._create_url(self.meter_ch1)
		
		self.ch2_url	= self.meter_ch2	and self._create_url(self.meter_ch2)	or ''
		self.aux1_url	= self.meter_aux1	and self._create_url(self.meter_aux1)	or ''
		self.aux2_url	= self.meter_aux2	and self._create_url(self.meter_aux2)	or ''
		self.aux3_url	= self.meter_aux3	and self._create_url(self.meter_aux3)	or ''
		self.aux4_url	= self.meter_aux4	and self._create_url(self.meter_aux4)	or ''
		self.aux5_url	= self.meter_aux5	and self._create_url(self.meter_aux5)	or ''

		self.call_period = MINUTE
		self.last_call = 0

	def _make_call(self, url, timestamp, magnitude):
		data = {
			'updates': [
				{
					'timestamp': timestamp,
					'power': {
						'magnitude':	int(magnitude), # truncated by WattzOn API, anyway
						'unit':			'W',
					}
				},
			]
		}

		req = RequestPostWithContentType('application/json', url, json.dumps(data))
		f = urllib2.urlopen(req)

		return f.read()
		
	def process(self, packet):
		super(WattzOnMixin, self).process(packet)

		now = int(time.time())
		if not self.last_call:
			self.last_call = now
			return
		if now < (self.last_call+self.call_period):
			return
		self.last_call = now

		timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
		try:
			delta = self.buffer.delta_over(self.call_period)
		except ZeroDivisionError, zde:
			return # not enough data in buffer
		
		result = self._make_call(self.ch1_url, timestamp, delta['ch1_watts'])
		if not self.quiet:
			print 'WattzOn: %s' % (timestamp,)
			print '  [%s] magnitude: %s w/ result: %s' % (
				self.meter_ch1, delta['ch1_watts'], result)

		for meter_type in ['ch2', 'aux1', 'aux2', 'aux3', 'aux4', 'aux5']:
			if getattr(self, meter_type+'_url', None) and delta[meter_type+'_watts']:
				result = self._make_call(
					getattr(self, meter_type+'_url'), timestamp, delta[meter_type+'_watts'])
				if not self.quiet:
					print '  [%s] magnitude: %s w/ result: %s' % (
						getattr(self, 'meter_'+meter_type), delta[meter_type+'_watts'], result)
		
	def handle(self, exception):
		if type(exception) == urllib2.HTTPError:
			print 'HTTPError: ', exception
			print '  URL:        ', self.update_url
			print '  username:   ', self.api_username
			print '  passwd:     ', self.api_passwd
			print '  API key:    ', self.api_key
			print '  powermeter: ', self.powermeter
			return True
		
		return super(WattzOnMixin, self).handle(exception)

if __name__ == '__main__':
	parser = optparse.OptionParser()

	parser.add_option('--serial', action='store_true', dest='serial_read', default=False, help='read from Serial Port')
	parser.add_option('--serialport', dest='serial_port', help='serial port')
	parser.add_option('-b', '--baudrate', dest='baudrate', help='baud rate')

	parser.add_option('--ip', action='store_true', dest='ip_read', default=False, help='read from EtherBee')
	parser.add_option('--host', dest='ip_host', help='ip host')
	parser.add_option('--port', dest='ip_port', help='ip port')

	parser.add_option('-p', '--print', action='store_true', dest='print_out', default=False, help='print data to screen')

	parser.add_option('-d', '--database', action='store_true', dest='db_write', default=False, help='write data to db')
	parser.add_option('--db-host', dest='db_host', help='db host')
	parser.add_option('--db-user', dest='db_user', help='db user')
	parser.add_option('--db-passwd', dest='db_passwd', help='db passwd')
	parser.add_option('--db-database', dest='db_database', help='db database')

	parser.add_option('--wattzon', action='store_true', dest='wattzon_out', default=False, help='upload data via WattzOn API')
	parser.add_option('--wattzon-user', dest='wattzon_user', help='WattzOn username')
	parser.add_option('--wattzon-pass', dest='wattzon_pass', help='WattzOn password')
	parser.add_option('--wattzon-key', dest='wattzon_key', help='WattzOn API key')
	parser.add_option('--wattzon-ch1', dest='wattzon_ch1', help='WattzOn powermeter name for CH1')
	parser.add_option('--wattzon-ch2', dest='wattzon_ch2', help='WattzOn powermeter name for CH2')
	parser.add_option('--wattzon-aux1', dest='wattzon_aux1', help='WattzOn powermeter name for AUX1')
	parser.add_option('--wattzon-aux2', dest='wattzon_aux2', help='WattzOn powermeter name for AUX2')
	parser.add_option('--wattzon-aux3', dest='wattzon_aux3', help='WattzOn powermeter name for AUX3')
	parser.add_option('--wattzon-aux4', dest='wattzon_aux4', help='WattzOn powermeter name for AUX4')
	parser.add_option('--wattzon-aux5', dest='wattzon_aux5', help='WattzOn powermeter name for AUX5')

	parser.add_option('-q', '--quiet', action='store_true', dest='quiet', default=False, help='quiet output')

	(options, args) = parser.parse_args()
	
	# Packet Processor Setup
	if not (options.print_out or options.db_write or options.wattzon_out):
		print 'Please choose a processing option (or \'-h\' for more help):'
		print '    -p        (print to screen)'
		print '    -d        (write to databse)'
		print '    --wattzon (update WattzOn)'
		sys.exit(1)

	buffer_timeframe = 5*MINUTE
	
	bases = [BaseProcessor]
	kwargs = {
		'quiet': options.quiet,
	}

	if options.print_out:
		bases.insert(0, PrintMixin)
	if options.db_write:
		bases.insert(0, DatabaseMixin)
		kwargs.update({
			'db_host':		options.db_host,
			'db_user':		options.db_user,
			'db_passwd':	options.db_passwd,
			'db_database':	options.db_database,
		})
	if options.wattzon_out:
		bases.insert(0, WattzOnMixin)
		kwargs.update({
			'api_key':		options.wattzon_key,
			'api_username':	options.wattzon_user,
			'api_passwd':	options.wattzon_pass,
			'meter_ch1':	options.wattzon_ch1,
			'meter_ch2':	options.wattzon_ch2,
			'meter_aux1':	options.wattzon_aux1,
			'meter_aux2':	options.wattzon_aux2,
			'meter_aux3':	options.wattzon_aux3,
			'meter_aux4':	options.wattzon_aux4,
			'meter_aux5':	options.wattzon_aux5,
		})

	Processor = new.classobj('Processor', tuple(bases), {})

	processor = Processor(
		buffer_timeframe,
		**kwargs)

	# Packet Server Setup
	if options.serial_read:
		options.serial_port	= options.serial_port	and options.serial_port	or SERIALPORT
		options.baudrate	= options.baudrate		and options.baudrate	or BAUDRATE
		
		server = SerialPacketServer(processor, options.serial_port, options.baudrate)

	elif options.ip_read:
		options.ip_host	= options.ip_host and options.ip_host or HOST
		options.ip_port = options.ip_port and options.ip_port or PORT

		server = SocketPacketServer(processor, options.ip_host, options.ip_port)	

	else:
		print 'Please choose a data feed (or \'-h\' for more help):'
		print '    --serial (read from serial)'
		print '    --ip     (read from EtherBee)'
		sys.exit(1)

	server.run()

	sys.exit(0)

