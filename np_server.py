#!/usr/bin/env python
from optparse import OptionParser
import socket
from time import sleep

pinAddr = ""
pintPort = 0

ftpUser =""
ftpPass ="" 

def testNatPin(ip,port):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	try:
		s.connect((ip,port))
		sleep(2)
		s.close()
		return "OK"
	except:
		return "ERR"

def ftpCalcPortNotation(port):
	x = port%256
	y = (port -x)/256
	return (y,x)

def ftpCalcPort(lsPortCommand):
	try:
		ls = lsPortCommand
		ls = ls.upper()
		ls = ls.replace("PORT","")
		ls = ls.strip()
		parts = ls.split(",")
		return int(parts[4])*256 + int(parts[5])
	except:
		return 0

def createFTP():
	s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
	s.bind(("",21))
	s.listen(1)
	while 1:
		cSock, cAddr = s.accept()
		cFile = cSock.makefile('rw',0)
		cFile.write("220 NATPinningTest\n")
		while 1:
			line = cFile.readline().strip()
			if (line[:4].upper() == "PORT"):
				#this is where we store callback port
				port = ftpCalcPort(line)
				if (port > 0 ):
					print "Callback expected on " + cAddr[0] + ":" + str(port)
					pinAddr = cAddr[0]
					pinPort = port
				else:
					print "Failed to calculate port from: " + line
				cFile.write("200 Let's do this\n")
			elif (line[:4].upper() == "USER"):
				ftpUser = line.upper().replace("USER","").strip()
				cFile.write("331 need pass\n")
			elif(line[:4].upper() == "PASS"):
				ftpPass = line.upper().replace("PASS","").strip()
				cFile.write("230 is good\n")
			elif(line[:4].upper() == "LIST"):
				cFile.write("150 opening data connection\n")
				#time to connect to specified port
				if testNatPin(pinAddr,pinPort) == "OK":
					print "NAT Pinning was succesfull"
				else:
					print "Test failed"
			elif(line[:4].upper()=="PASV"):
				portspecs = ftpCalcPortNotation(int(ftpPass))
				print "Trying pasv pinning on " + ftpUser +":"+ftpPass
				cFile.write("227 Entering passive mode ("+ ftpUser.replace(".",",") + ","+str(portspecs[0])+","+str(portspecs[1])+").\n")
			elif(line[:4].upper() == "QUIT"):
				cFile.write("221 byebye\n")
				cFile.close()
				s.close
				return 0
			else:
				cFile.write("200 it's all good\n")

def setupServer(sType):
	if (sType=="FTP"):
		s = createFTP()


setupServer("FTP")
