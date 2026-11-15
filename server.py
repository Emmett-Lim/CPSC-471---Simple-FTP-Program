# *********************************************************************
# {=== Server Script ===}
# 
# Usage: python/python3/py server.py [port_num]
#
# Description: Should listen and wait for client's connection. Client
# can pull or put data (textfile) into server's directory, ServerDir.
# *********************************************************************

import socket
import sys
import os


# {=== Command Line Checker ===}
if len(sys.argv) != 2:
    print("USAGE: python/python3/py " + sys.argv[0] + " [port_num]")
    sys.exit(1)

listenPort = int(sys.argv[1])



# {=== Helper Functions ===}
# Receive specified number of bytes from specified socket
def recvAll(sock, numBytes):
    recvBuff = bytes()
    tmpBuff = bytes()

    while len(recvBuff) < numBytes:
        tmpBuff = sock.recv(numBytes - len(recvBuff))
    
        if not tmpBuff:
            break
        recvBuff += tmpBuff

    return recvBuff

# Send every byte (may send fewer than requested)
def sendAll(sock, data):
    numSent = 0

    while numSent < len(data):
        numSent += sock.send(data[numSent:])

# Send a message (Format: 10-byte padding + data)
def sendMsg(sock, data):
    if isinstance(data, str):
        data = data.encode()

    header = str(len(data)).zfill(10).encode()
    sendAll(sock, header + data)

# Receive a message
def recvMsg(sock):
    header = recvAll(sock, 10)

    if len(header) < 10:
        return None
    
    return recvAll(sock, int(header))

# Open data channel by connecting to client's port
def openDataChannel(clientIP, dataPort):
    dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataSock.connect((clientIP, dataPort))
    return dataSock



# {=== Handle Command Functions===}
# Status update through control channel. Transfer a file on data channel if good to go.

# List of what files are in ServerDir
def doLs(ctrlSock, clientIP, dataPort):
    listing = "\n".join(sorted(os.listdir("ServerDir")))
    sendMsg(ctrlSock, "SUCCESS")

    dataSock = openDataChannel(clientIP, dataPort)
    sendMsg(dataSock, listing)
    dataSock.close()

    print("ls: SUCCESS")

# Get file from ServerDir and send to client
def doGet(ctrlSock, clientIP, dataPort, fileName):
    # This removes other parts of directory so client can't full path
    fileName = os.path.basename(fileName)
    filePath = os.path.join("ServerDir", fileName)
    
    if not os.path.isfile(filePath):
        sendMsg(ctrlSock, "FAILURE File not found: " + fileName)
        print("get " + fileName + ": FAILURE (file not found)")
        return
    
    sendMsg(ctrlSock, "SUCCESS")

    with open(filePath, "rb") as f:
        fileData = f.read()
    
    dataSock = openDataChannel(clientIP, dataPort)
    sendMsg(dataSock, fileData)
    dataSock.close()

    print("get " + fileName + ": SUCCESS (" + str(len(fileData)) + " bytes)")

# Retreive a file sent from sender/client
def doPut(ctrlSock, clientIP, dataPort, fileName):
    fileName = os.path.basename(fileName)
    
    sendMsg(ctrlSock, "SUCCESS")

    dataSock = openDataChannel(clientIP, dataPort)
    fileData = recvMsg(dataSock) # Remember: (padding + data)
    dataSock.close()

    if fileData is None:
        print("put " + fileName + ": FAILURE (connection lost)")
        return

    savePath = os.path.join("ServerDir", fileName)
    with open(savePath, "wb") as f:
        f.write(fileData)
    
    print("put " + fileName + ": SUCCESS (" + str(len(fileData)) + " bytes)")



# {=== Main Function of Sever === }
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcomeSock.bind(('', listenPort))
welcomeSock.listen(1)

print("Server listening on port " + str(listenPort))

while True:
    print("Waiting for connections...")
    ctrlSock, addr = welcomeSock.accept()
    clientIP = addr[0]
    print("Accepted connection from client: " + str(addr))

    while True:
        msg = recvMsg(ctrlSock)

        if msg is None:
            break

        parts = msg.decode().split(" ", 2)
        cmd = parts[0]

        if cmd == "quit":
            print("quit: SUCCESS")
            break
        try:
            if cmd == "ls":
                doLs(ctrlSock, clientIP, int(parts[1]))
            elif cmd == "get":
                doGet(ctrlSock, clientIP, int(parts[1]), parts[2])
            elif cmd == "put":
                doPut(ctrlSock, clientIP, int(parts[1]), parts[2])
            else:
                sendMsg(ctrlSock, "FAILURE Unknown command")
                print(cmd + ": FAILURE (unknown command)")
        except (IndexError, ValueError, OSError) as e:
            print(cmd + ": FAILURE (" + str(e) + ")")

    ctrlSock.close()
    print("Client has disconnected.\n")