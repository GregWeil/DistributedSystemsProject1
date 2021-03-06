#A generic distributed network framework

import socket
import threading
import pickle

class Peer(object):
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
	
	def __str__(self):
		return self.ip + ':' + str(self.port)
	
	def addr(self):
		return (self.ip, self.port)

class Network(object):
	def __init__(self, config, node):
		self.peer = []
		self.node = node
		self.recv = None
		#Load config
		self.loadConfig(config)
		#Create a socket
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.bind(('', self.peer[self.node].port))
		#Create a thread for the socket
		self.thread = threading.Thread(target = self.listen)
		self.thread.setDaemon(True)
		self.thread.start()
	
	def loadConfig(self, path):
		"""Load the network config file"""
		"""It is a set of addresses separated by newlines"""
		f = open(path, 'r')
		for l in f.read().split('\n'):
			if l:
				d = l.split(':')
				self.peer.append(Peer(d[0], int(d[1])))
	
	def registerReceive(self, func):
		"""Register a function to call on message receipt"""
		"""The node index and message will be passed to it"""
		self.recv = func
	
	def listen(self):
		"""Poll the socket for incoming messages"""
		"""Run on a separate thread"""
		while True:
			try:
				data, addr = self.socket.recvfrom(4096)
				for i in range(len(self.peer)):
					if self.peer[i].addr() != addr:
						continue
					self.receive(i, data)
					break
			except socket.error as error:
				pass
	
	def receive(self, node, message):
		"""A message has been received"""
		if self.recv: self.recv(node, pickle.loads(message))
	
	def send(self, message, targets = None):
		"""Send a message to some or all peers"""
		if not targets:
			targets = range(len(self.peer))
		targets = [self.peer[i] for i in targets if i != self.node]
		data = pickle.dumps(message)
		for p in targets:
			sent = self.socket.sendto(data, p.addr())
			if sent != len(data):
				print(send, len(data))
