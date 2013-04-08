These are POC scripts to test natpinning on routers.

Eventually these will be bundeled into one tool that you can use to test all possible loaded helper modules on a router to determine which ones are loaded.
In a later stage basi tests will be performed to test the security implementation on the loaded modules.:
	-e.g. does it trigger port forwarding after a single line
	-does it simply ignore invalid statements
	-where ip's are specified in the protocol (i.e.: IRC), does it allow portforwarding to a third host
	-if it allows forwarding to a third host, does it allow forwarding to itself
	-are the helpers security config parameters set correctly

The setup will allways be the same, client modules are loaded on a host on the target natted LAN, the servr is set up on a remote server.
Once the client and server are communicating and one of them triggers the nat pinning/port forwarding, an automatic connect test to the forwarded port will be made to validate wether the test was 
succesfull.

Credits: original NAT  pinning POC by Smy Kamkar: http://samy.pl/natpin/


Current status:
 - arough first IRC test is created, follows a fully correct irc conversation up to a DCC chat request
 - a ftp server is created that supports natpinning test through PASV command and PORT command
 
 
