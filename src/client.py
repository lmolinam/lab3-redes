import socket
 
def main():
        host = '127.0.0.1'
        port = 6060
         
        mySocket = socket.socket()
        mySocket.connect((host,port))
         
        message = input(" -> ")
         
        while message != 'q':
                mySocket.send(message.encode())
                data = mySocket.recv(1024).decode()

                if not data:
                    print("Conexión terminada por parte de servidor")
                    break
                 
                print ('Received from server: ' + data)
                 
                message = input(" -> ")
                 
        mySocket.close()
 
if __name__ == '__main__':
    main()