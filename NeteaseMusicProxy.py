from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
from twisted.python.compat import urllib_parse
from io import StringIO
import sys, gzip, os, time
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
	if res.startswith(b'gzip'):
		return None
	return res

def modify_response(response):
	response = response.replace(b'"st":-100', b'"st":0')
	response = response.replace(b'"st":-200', b'"st":0')
	response = response.replace(b'"pl":0', b'"pl":320000')
	response = response.replace(b'"dl":0', b'"dl":320000')
	response = response.replace(b'"fl":0', b'"fl":320000')
	response = response.replace(b'"sp":0', b'"sp":7')
	response = response.replace(b'"cp":0', b'"cp":1')
	response = response.replace(b'"subp":0', b'"subp":1')
	return response

class MainlandProxy():
	def __init__(self):
		self.default_ip = '123.57.215.44'
		self.default_port = 32796
		self.ip = ''
		self.port = -1
		self.failed_times = 0
		self.set_proxy()
		self.status = 0
		self.url_request_lengths = [b'296', b'264', b'168']

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
		if self.ip == ip and self.port == port:
			self.set_to_default()
		else:
			self.ip = ip
			self.port = port

	def set_to_default(self):
		self.ip, self.port = self.default_ip, self.default_port

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
			self.intercept = {'song': b'/eapi/v3/song/detail/', 'search': b'/eapi/cloudsearch/pc', 'url': b'/eapi/song/enhance/player/url', 'album': b'/eapi/v1/album', 'artist': b'/eapi/v1/artist', 'playlist': b'/eapi/v3/playlist/detail', 'discovery': b'/eapi/v1/discovery/new/songs', 'linux': b'/api/linux/forward'}
			self.interval = {self.intercept['song']: 10, self.intercept['search']: 100, 'default': 10}
			self.temp_buffer = {self.intercept['song']: None, self.intercept['search']: None}
			self.timestamp = {self.intercept['song']: time.time(), self.intercept['search']: time.time()}
			proxy.ProxyClient.__init__(self, *args, **kwargs)

		def check_buffer(self, buffer):
			if (len(buffer) != 352):
				print('length of buffer:', len(buffer))
				mainland_proxy.change()
			else:
				mainland_proxy.status = 0

		def handleResponsePart(self, buffer):
			if self.rest in [self.intercept['song'], self.intercept['search'], self.intercept['playlist'], self.intercept['discovery'], self.intercept['linux']] or self.intercept['album'] in self.rest or self.intercept['artist'] in self.rest:
				if True: #self.headers['content-length'] not in mainland_proxy.url_request_lengths:
					print('response intercepted: ', self.rest)
					if self.rest not in self.timestamp:
						self.timestamp[self.rest] = time.time()
						self.temp_buffer[self.rest] = None
					if time.time() - self.timestamp[self.rest] > self.interval.get(self.rest, self.interval['default']):
						self.temp_buffer[self.rest] = 0
						self.timestamp[self.rest] = time.time()
					if self.temp_buffer[self.rest] != None:
						buffer = self.temp_buffer[self.rest] + buffer
					buffer_str = sh_gzip_decompress(buffer)
					if buffer_str == None or b'unexpected end of file' in buffer_str:
						self.temp_buffer[self.rest] = buffer
						self.timestamp[self.rest] = time.time()
						return
					else:
						del self.temp_buffer[self.rest]
						del self.timestamp[self.rest]
					buffer_str = modify_response(buffer_str)
					#print buffer_str
					buffer = sh_gzip_compress(buffer_str)
			if self.rest == self.intercept['url']:
				self.check_buffer(buffer)
			proxy.ProxyClient.handleResponsePart(self, buffer)

class NeteaseMusicProxyClientFactory(proxy.ProxyClientFactory):
	protocol = NeteaseMusicProxyClient
	def clientConnectionFailed(self, connector, reason):
		print reason, 'client connection failed, changing proxy'
		mainland_proxy.change()
	def clientConnectionLost(self, connector, reason):
		if mainland_proxy.status == -1:
			print('audio request no response, changing proxy')
			mainland_proxy.change()
			mainland_proxy.status = 0

class NeteaseMusicProxyRequest(proxy.ProxyRequest):
	protocols = {b'http': NeteaseMusicProxyClientFactory}

	def process_prepare(self):
		# print self.method, self.uri, self.path, self.args, self.requestHeaders, self.responseHeaders, self.received_cookies, self.protocols, self.host, self.channel, self.content, self.cookies
		parsed = urllib_parse.urlparse(self.uri)
		protocol = parsed[0] or 'http'
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
		return host, port, clientFactory

	def process(self):
		if self.uri == b'music.163.com:443':
			print('DEBUG: Abort on request:', self.uri)
			self.channel._respondToBadRequestAndDisconnect()
			return
		host, port, clientFactory = self.process_prepare()
		print(self.uri)
		if self.uri == b'http://music.163.com/eapi/song/enhance/player/url' or self.uri == b'http://music.163.com/api/linux/forward' and self.getHeader('content-length') in mainland_proxy.url_request_lengths:
			print('request intercepted:', self.uri, self.getHeader('content-length'))
			#mainland_proxy.set_to_default()
			mainland_proxy.status = -1
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
