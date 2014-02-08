NATpinning
===============
This tool is based of the original NAT pinning proof-of-concept by Samy Kamkar: http://samy.pl/natpin/.

Samy's original proof-of-concept was javascript based, which brought with it several shortcommings:

	- client-response sequences might be broken due to additional HTTP headers
	- opening some ports might be blocked by browsers (e.g.: 6667 for irc on Firefox)

To overcome these issues we switched to flash as client side component. This allowed the use of Flash sockets, which don't have the extra overhead of HTTP headers and are not restricted by browser policies. 

We also attempted to extend this proof-of-concept to a more mature state by adding support for more protocols and creating a server side tool which gives some level of control over the client behavior.


How it works
============
The application consists of of a server compnent (python) and a client component (web page).

The server is a python script which needs to be run from an Internet based host, with a public IP assigned to it and not firewalled.
Once the script is running it will open dummy services (irc, ftp, sip ), a flash policy server and a web service.

The client is the combination of HTML, JavaScript and, most importantly, a AS3 (Actionscript 3) flash file. 

Installation
==============
Tested on xubuntu and backtrack, requires python 2.7
to install:
```
git clone https://github.com/allodoxaphobia/natpinning.git
```


Usage
==============
```
Usage:  sudo ./run.py
	sudo ./run.py --web-port 8080
	sudo ./run.py (-h | --help)

Options:
  -h, --help          show this help message and exit
  --no-web            Do not run the internal web service (port 80).
  --no-flash          Do not run the internal flash policy service (port 843).
  --web-port=WEBPORT  Specify different port for webserver.
  --no-ip             Don' call external URLs to determine ip.
  -v VERBOSE          Verbosity level, default is 0, set to 5 if you like a
                      lot of output.
```

License
==============
This tool was created by Gremwell (http://www.gremwell.com) and released under GNU GPL v3. 
