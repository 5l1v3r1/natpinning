#!/usr/bin/env python
#filename=ftp.py
from base import *
import struct

class Client(Base):
	def __init__(self,selfserverIp, serverPort, sCallbackip,iCallbackPort):
		Base.__init__(self,"TCP",selfserverIp, serverPort, sCallbackip,iCallbackPort)
	#end def
	def protocolhandler(self):
		while 1:		#runs on seperate thread, will be killed when callback results are in
			indata = self.sSock.recv(1024).split('\r\n')
			for line in indata:
				x = line.split(" ",2)
				if x[0] == "220": #server banner
					self.sSock.send("USER anonymous\r\n")
				elif x[0] == "331": #send pass
					self.sSock.send("PASS natpin@work.net\r\n")
				elif x[0] == "230": #logged in succesfully
					cmd = "PORT " + self.cbIp.replace(".",",")
					for val in self.ftpCalcPortNotation(self.cbPort):
						cmd = cmd + "," + str(val)
					self.sSock.send(cmd + "\r\n")
				elif x[0] == "200": #last cmd succesfull, send list
					self.sSock.send("LIST\r\n") #after this command is send, the server will try connecting on callback port
	#end def

	def ftpCalcPortNotation(self,port):
		x = port%256
		y = (port -x)/256
		return (y,x)
	#end def
#end class
