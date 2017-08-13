from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
from twisted.python.compat import urllib_parse
import sys, gzip, StringIO, os, time
from subprocess import Popen, PIPE, STDOUT
import requests
from pyquery.pyquery import PyQuery

log.startLogging(sys.stdout)

def py_gzip_compress(plain_content):
	temp_file = StringIO.StringIO()
	with gzip.GzipFile(fileobj=temp_file, mode="w") as f:
		f.write(plain_content)
		return temp_file.getvalue()

def py_gzip_decompress(compressed_content):
	temp_file = StringIO.StringIO()
	temp_file.write(compressed_content)
	temp_file.seek(0)
	with gzip.GzipFile(fileobj=temp_file, mode="rb") as f:
		return f.read()

def sh_gzip_compress(plain_content):
	p = Popen(['gzip', '-c'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	return p.communicate(input=plain_content)[0]

def sh_gzip_decompress(compressed_content):
	p = Popen(['gzip', '-dc'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	res = p.communicate(input=compressed_content)[0]
	if res.startswith("gzip"):
		return None
	return res

def modify_response(response):
	response = response.replace('"st":-100', '"st":0')
	response = response.replace('"st":-200', '"st":0')
	response = response.replace('"pl":0', '"pl":320000')
	response = response.replace('"dl":0', '"dl":320000')
	response = response.replace('"fl":0', '"fl":320000')
	response = response.replace('"sp":0', '"sp":7')
	response = response.replace('"cp":0', '"cp":1')
	response = response.replace('"subp":0', '"subp":1')
	return response

class MainlandProxy():
	def __init__(self):
		self.default_ip = '123.57.215.44'
		self.default_port = 32796
		self.ip = ''
		self.port = -1
		self.failed_times = 0
		self.set_proxy()

	def set_proxy(self):
		r = requests.get("http://cn-proxy.com/")
		q = PyQuery(r.content)
		trs = q("tbody tr")
		if (len(trs) == 0):
			self.ip = self.default_ip
			self.port = self.default_port
			return
		tr = trs[min(self.failed_times,len(trs)-1)]
		trq = PyQuery(tr)
		tds = trq.children()
		ip = tds.eq(0).text()
		port = int(tds.eq(1).text())
		self.ip = ip
		self.port = port

	def change(self):
		self.failed_times += 1
		print('bad proxy, ip: %s port: %d' % (self.ip, self.port))
		if (self.failed_times > 5 and self.ip != self.default_ip):
			self.failed_times = 0
			self.ip = self.default_ip
			self.port = self.default_port
		else:
			self.set_proxy()
		print("using ip %s and port %d" % (self.ip, self.port))

	def check(self, buffer_str):
		for msg in ['HTTP Status 404', 'ERROR', 'ERR_INVALID_URL', 'Internal Server Error']:
			if msg in buffer_str:
				self.change()
				break


class NeteaseMusicProxyClient(proxy.ProxyClient):
		def __init__(self, *args, **kwargs):
			self.intercept = {'song': '/eapi/v3/song/detail/', 'search': '/eapi/cloudsearch/pc', 'url': '/eapi/song/enhance/player/url'}
			self.interval = {self.intercept['song']: 10, self.intercept['search']: 100}
			self.temp_buffer = {self.intercept['song']: None, self.intercept['search']: None}
			self.timestamp = {self.intercept['song']: time.time(), self.intercept['search']: time.time()}
			proxy.ProxyClient.__init__(self, *args, **kwargs)

		def check_buffer(self, buffer):
			if (len(buffer) != 352):
				print 'length of buffer:', len(buffer)
				mainland_proxy.change()
			# try:
			# 	print buffer
			# 	mainland_proxy.check(buffer)
			# 	return
			# except:
			# 	print 'url direct read failed'
			# try:
			# 	buffer_str = buffer.encode('utf-8')
			# 	print buffer_str
			# 	mainland_proxy.check(buffer_str)
			# 	return
			# except UnicodeDecodeError:
			# 	print 'url utf-8 encode failed'
			# buffer_str = sh_gzip_decompress(buffer)
			# if buffer_str is not None:
			# 	print buffer_str
			# 	mainland_proxy.check(buffer_str)
			# else:
			# 	print 'url gzip decompress failed'

		def handleResponsePart(self, buffer):
			if self.rest in [self.intercept['song'], self.intercept['search']]:
				print('response intercepted: ' + self.rest)
				if time.time() - self.timestamp[self.rest] > self.interval[self.rest]:
					self.temp_buffer[self.rest] = 0
					self.timestamp[self.rest] = time.time()
				if self.temp_buffer[self.rest] != None:
					buffer = self.temp_buffer[self.rest] + buffer
				buffer_str = sh_gzip_decompress(buffer)
				if buffer_str == None or 'unexpected end of file' in buffer_str:
					self.temp_buffer[self.rest] = buffer
					self.timestamp[self.rest] = time.time()
					return
				else:
					self.temp_buffer[self.rest] = None
					self.timestamp[self.rest] = time.time()
				buffer_str = modify_response(buffer_str)
				#print buffer_str
				buffer = sh_gzip_compress(buffer_str)
			if self.rest == self.intercept['url']:
				self.check_buffer(buffer)
			# if self.rest == '/eapi/song/like':
			# 	buffer_str = sh_gzip_decompress(buffer)
			# 	print buffer_str
			# 	buffer = sh_gzip_compress('{"playlistId":0,"code":200}')
			# if self.rest == '/eapi/v1/playlist/manipulate/tracks':
			# 	buffer_str = sh_gzip_decompress(buffer)
			# 	buffer_str = buffer_str.replace('"code":401', '"code":200')
			# 	# buffer_str = buffer_str.replace('"count":269', '"count":270')
			# 	print buffer_str
			# 	buffer = sh_gzip_compress(buffer_str)
			proxy.ProxyClient.handleResponsePart(self, buffer)

class NeteaseMusicProxyClientFactory(proxy.ProxyClientFactory):
	protocol = NeteaseMusicProxyClient

class NeteaseMusicProxyRequest(proxy.ProxyRequest):
	protocols = {b'http': NeteaseMusicProxyClientFactory}

	def process_prepare(self):
		parsed = urllib_parse.urlparse(self.uri)
		protocol = parsed[0]
		host = parsed[1].decode('ascii')
		port = self.ports[protocol]
		if ':' in host:
			host, port = host.split(':')
			port = int(port)
		rest = urllib_parse.urlunparse((b'', b'') + parsed[2:])
		if not rest:
			rest = rest + b'/'
		class_ = self.protocols[protocol]
		headers = self.getAllHeaders().copy()
		if b'host' not in headers:
			headers[b'host'] = host.encode('ascii')
		self.content.seek(0, 0)
		s = self.content.read()
		clientFactory = class_(self.method, rest, self.clientproto, headers, s, self)
		# if self.uri == 'http://music.163.com/eapi/song/like':
		# 	print rest, headers, s
		# if self.uri == 'http://music.163.com/eapi/v1/playlist/manipulate/tracks':
		# 	print rest, headers, s
		return host, port, clientFactory

	def process(self):
		if self.uri == 'music.163.com:443':
			print('DEBUG: Abort on request: ' + self.uri)
			self.channel._respondToBadRequestAndDisconnect()
			return
		host, port, clientFactory = self.process_prepare()
		if self.uri == 'http://music.163.com/eapi/song/enhance/player/url':
			print('request intercepted: ' + self.uri)
			#mainland_proxy.ip, mainland_proxy.port = mainland_proxy.default_ip, mainland_proxy.default_port
			self.reactor.connectTCP(mainland_proxy.ip, mainland_proxy.port, clientFactory)
			return
		self.reactor.connectTCP(host, port, clientFactory)

class NeteaseMusicProxy(proxy.Proxy):
	requestFactory = NeteaseMusicProxyRequest

class NeteaseMusicProxyFactory(http.HTTPFactory):
	protocol = NeteaseMusicProxy

mainland_proxy = MainlandProxy()
reactor.listenTCP(32794, NeteaseMusicProxyFactory())
reactor.run()
