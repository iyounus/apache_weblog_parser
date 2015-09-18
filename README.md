# Apache Web Log Parser

This code snippet parses the apche web log, to extract the following informaion:

Remote host (ie the client IP)  
Time the server finished processing the request.  
Request line from the client. ("GET / HTTP/1.0")  
Referer is the page that linked to this URL.  

It then obtains the location information for the ip address using the api provided by [APIgurus](http://www.apigurus.com/). Finally it writes a csv file with the following information:

date & time request was processed by the web server as epoch  
uri user click on (from the log file)  
referer (from the log file)  
ip address (from the log file)  
organization (from the ip address)  
latitude (from the ip address)  
longitude (from the ip address)  
isp name (from the ip address)  
