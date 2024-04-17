import socket
from time import sleep

# Server's IP address and port
server_ip = '10.0.6.126'
server_port = 9999

# Create a socket object
client_socket = socket.socket()

# Connect to the server
client_socket.connect((server_ip, server_port))

# Receive the welcome message from the server
welcome_message = client_socket.recv(1024).decode()
print(welcome_message)

# Loop to continuously receive input from the server
while True:
    # Receive data from the server
    data = client_socket.recv(1024).decode()
    
    # Check if the received data is empty
    if not data:
        break
    
    # Print the received data
    print(data)

# Close the connection
#client_socket.close()

for x in range(10000):
    try:
        client_socket.send(('This is super super super long text, how I expect ASR will be or similar. Some sort of quick redf fox jumped over a log or something.  ' + str(x)).encode()) 
    except:
        break
    sleep(1)

# Close the connection with the client 
client_socket.close()
