from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
from twisted.python.compat import urllib_parse
import sys

log.startLogging(sys.stdout)

class AudioProxyRequest(proxy.ProxyRequest):
	#protocols = {b'': proxy.ProxyClientFactory, b'http': proxy.ProxyClientFactory}

	def process(self):
		self.uri = 'http://music.163.com' + self.uri
		print(self.uri)
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
		#print('host: '+str(host)+', port: '+str(port))
		#print(headers)
		self.reactor.connectTCP(host, port, clientFactory)

class AudioProxy(proxy.Proxy):
	requestFactory = AudioProxyRequest

class ProxyFactory(http.HTTPFactory):
	protocol = AudioProxy

reactor.listenTCP(32796, ProxyFactory())
reactor.run()