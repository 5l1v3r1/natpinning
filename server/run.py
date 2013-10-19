#!/usr/bin/env python
from modules import irc
from modules import ftp
from modules import flashpol
from modules import web
from modules import sip
from modules import cmd
from optparse import OptionParser
from tools import ip
import sys
import asyncore
import thread

class Shell():
	ENGINE = None
	CURR_VICTIM = None
	def __init__(self, engine):
		global ENGINE
		self.ENGINE = engine
		print "One shell to rule them all"
		val = ""
		while val.upper() != "QUIT" and val.upper() != "EXIT":
			val = self.getUserInput()
			self.handleCMD(val)
		self.ENGINE.shutdown()
		#end while
	#end def
	############################################################################
	def getVictims(self):
		for server in self.ENGINE.SERVERS:
			if server.TYPE=="COMMAND Server":
				if server.HANDLER:
					return server.HANDLER.VICTIMS
				else:
					return []
	def getVictimById(self,id):
		victims = self.getVictims()
		return victims[id]
	############################################################################
	def handleCmd_test(self, args):
		format ="test VICTIM_ID PROTO IP PORT"
		if len(args) != 5:
			print "invalid command format, expected : " + format
		else:
			vic_id = int(args[1])
			proto = args[2].upper()
			ip = args[3]
			port = args[4]
			victim = self.getVictimById(vic_id)
			victim.TESTS.append(proto + " " +  ip + " " + str(port))
	def handleCmd_list(self, item):
		if item.upper()=="VICTIMS":
			victims = self.getVictims() # refresh list
			x = 0
			for victim in victims:
				print "   " + str(x) + ".   " + victim.VIC_ID + "\t\t" + victim.PUBLIC_IP
				x=x+1
		elif item.upper() =="SERVICES":
			print "Currently running services:"
			x = 0
			for server in self.ENGINE.SERVERS:
				print "\t" + str(x) + ".\t" + server.TYPE
				x=x+1
				
		else:
			print "Invalid list item specified, allowed values are: victims, services"
	def getUserInput(self):
		prompt = "np> "
		user_input = raw_input(prompt).strip()
		return user_input
	def handleCMD(self,val):
		global CURR_VICTIM
		parts = val.split(" ")
		if parts[0].upper()=="LIST":
			if len(parts)==2:
				self.handleCmd_list(parts[1])
			else:
				self.handleCmd_list("unkown")
		elif parts[0].upper()=="SET":
			if len(parts)==3:
				if parts[1].upper() == "VIC":
					self.CURR_VICTIM = int(parts[2])
					print "Current victim set to " +  self.getVictimById(self.CURR_VICTIM).VIC_ID
		elif parts[0].upper()=="TEST":
			self.handleCmd_test(parts)
	#end def
#end class

class Engine():
	VERBOSITY = 2
	LOGTYPE = "screen"
	SERVERS = []
	SERVICE_THREAD = None
	def __init__(self, verbosity=0, logType="screen"):
		global VERBOSITY, LOGTYPE
		VERBOSITY = verbosity
		LOGTYPE = logType #either "screen" or filename
	#end def
	
	def log(self, value, logLevel):
		if logLevel >= self.VERBOSITY:
			print value
		#end if
	#end def
	def callback(self, host, port, proto):
		if ip.isPrivateAddress(host)==True:
			print "Can't perform callback on private ip " + host
		else:
			print "Todo: actuially call back"
	#end def
	def runServers(self,runCMD,runWeb, runFlash, proto="ALL"):
		global SERVERS, SERVICE_THREAD
		if runCMD == True: self.SERVERS.append(cmd.Server(proto="TCP",serverPort=60003,caller=self))
		if (runWeb==True): self.SERVERS.append(web.Server(serverPort=80,caller=self))#required: flash policy server
		if (runFlash==True): self.SERVERS.append(flashpol.Server(serverPort=843,caller=self))
		if proto== "FTP" or proto== "ALL":
	        	self.SERVERS.append(ftp.Server(serverPort=21,caller=self))
		if proto== "IRC" or proto== "ALL":
			self.SERVERS.append(irc.Server(serverPort=6667,caller=self))
		if proto ==  "SIP" or proto==  "ALL":
			self.SERVERS.append(sip.Server(serverPort=5060,caller=self))
		try:
			self.log("Services running, press CTRL-C to exit.",0)
			self.SERVICE_THREAD = thread.start_new_thread(asyncore.loop,()) #XXX TODO BLOCKING
		except KeyboardInterrupt:
			self.shutdown()
	#end def
	def shutdown(self):
		global SERVICE_THREAD
		for server in self.SERVERS:
			server.stop()
		self.SERVICE_THREAD = None
	#end def
#end class


x = Engine(0,"screen")
x.runServers(True,True,True,"ALL")
s = Shell(x)

