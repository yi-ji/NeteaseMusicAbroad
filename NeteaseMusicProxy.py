from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
from twisted.python.compat import urllib_parse
import sys, gzip, StringIO, os
from subprocess import Popen, PIPE, STDOUT

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
	# with open('song', 'wb') as f:
	# 	f.write(plain_content)
	# os.system('gzip song')
	# with open('song.gz', 'rb') as f:
	# 	return f.read()
	p = Popen(['gzip', '-c'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	return p.communicate(input=plain_content)[0]

def sh_gzip_decompress(compressed_content):
	# with open('song.gz', 'wb') as f:
	# 	f.write(compressed_content)
	# os.system('gzip -d song.gz')
	# with open('song', 'rb') as f:
	# 	return f.read()
	p = Popen(['gzip', '-dc'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
	return p.communicate(input=compressed_content)[0]

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

class NeteaseMusicProxyClient(proxy.ProxyClient):
	def handleResponsePart(self, buffer):
		if (self.rest == '/eapi/v3/song/detail/'):
			print('response intercepted: ' + self.rest)
			try:
				buffer_str = sh_gzip_decompress(buffer)
				buffer_str = modify_response(buffer_str)
				buffer = sh_gzip_compress(buffer_str)
			except IOError:
				print('bad response, cannot decompress')
		proxy.ProxyClient.handleResponsePart(self, buffer)

class NeteaseMusicProxyClientFactory(proxy.ProxyClientFactory):
	protocol = NeteaseMusicProxyClient

class NeteaseMusicProxyRequest(proxy.ProxyRequest):
	protocols = {b'http': NeteaseMusicProxyClientFactory}

	def process_audio(self):
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
		self.reactor.connectTCP("123.57.215.44", 32796, clientFactory)
		#print(headers)
		#print('method: '+self.method+'\ncontent:\n'+s)


	def process(self):
		if (self.uri == 'music.163.com:443'):
			print('DEBUG: Abort on request: ' + self.uri)
			self.channel._respondToBadRequestAndDisconnect()
			return
		if (self.uri == 'http://music.163.com/eapi/song/enhance/player/url'):
			print('request intercepted: ' + self.uri)
			self.process_audio()
			return
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
		self.reactor.connectTCP(host, port, clientFactory)

class NeteaseMusicProxy(proxy.Proxy):
	requestFactory = NeteaseMusicProxyRequest

class NeteaseMusicProxyFactory(http.HTTPFactory):
	protocol = NeteaseMusicProxy


reactor.listenTCP(32794, NeteaseMusicProxyFactory())
reactor.run()