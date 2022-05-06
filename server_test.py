#socket_echo_server.py

import socket,errno
import sys

def getPort():

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    port=8200

    while True:

        # Bind the socket to the port
        server_address = ('localhost', port)
        #print('starting up on {} port {}'.format(*server_address))

        try:
            sock.bind(server_address)
            print (port)
            sock.close()  # closing, I will reopen it afterwards
            return port
            exit()
            
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                #print("Port",port," is already in use,trying ",port+1)
                port+=1
            
            else:
                # something else raised the socket.error exception
                print(e)

            exit()
    return None

if __name__ == '__main__':
    getPort()
    

