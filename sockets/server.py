import socket 
from time import sleep    

# first of all import the socket library 

server_ip = '10.0.5.70'
server_port = 9999
    

# next create a socket object 
s = socket.socket()         
print ("Server Socket successfully created")
 
# reserve a port on your computer in our 
# case it is 9999 but it can be anything 
 
# Next bind to the port 
# we have not typed any ip in the ip field 
# instead we have inputted an empty string 
# this makes the server listen to requests 
# coming from other computers on the network 
s.bind((server_ip, server_port))         
print ("socket binded to %s" %(server_port)) 
print ("socket binded to %s" %(server_ip))
 
# put the socket into listening mode 
s.listen(5)     
print ("socket is listening")            

while True:
  c, addr = s.accept()  
  print ('Got connection from', addr )

  c.send('Thank you for connecting'.encode())

  data = c.recv(1024).decode()
  if not data:
    break

  print(data)

  # Close the connection with the client 
  c.close()