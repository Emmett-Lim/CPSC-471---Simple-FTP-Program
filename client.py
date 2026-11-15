# *********************************************************************
# {=== Client Script ===}
# 
# Usage: python/python3/py client.py [server port]
# Commands: get [file] | put [file] | ls | quit
#
# Description: Should send request to establish connection with the
# server. Can push or pull data (textfile) from server.
# *********************************************************************

import socket
import sys
import os



# {=== Command Line Checker ===}
if len(sys.argv) != 3:
    print("USAGE: python/python3/py " + sys.argv[0] + " [server machine] [server port]")
    sys.exit(1)

serverName = sys.argv[1]
serverPort = int(sys.argv[2])



# {=== Helper Functions ===}
def recvAll(sock, numBytes):
    recvBuff = bytes()
    tmpBuff = bytes()

    while len(recvBuff) < numBytes:
        tmpBuff = sock.recv(numBytes - len(recvBuff))

        if not tmpBuff:
            break
        recvBuff += tmpBuff

    return recvBuff

def recvMsg(sock):
    header = recvAll(sock, 10)

    if len(header) < 10:
        return None
    
    return recvAll(sock, int(header))

def sendAll(sock, data):
    numSent = 0

    while numSent < len(data):
        numSent += sock.send(data[numSent:])

def sendMsg(sock, data):
    if isinstance(data, str):
        data = data.encode()

    header = str(len(data)).zfill(10).encode()
    sendAll(sock, header + data)



# {=== Data Listener (Ephemeral Port) ===}
def makeDataListener():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('', 0))
    listener.listen(1)
    return listener, listener.getsockname()[1]



# {=== Command Handlers===}
# Ask server for a listing of their ServerDir
def lsCmd(ctrlSock):
    listener, port = makeDataListener()
    sendMsg(ctrlSock, "ls " + str(port))
    status = recvMsg(ctrlSock).decode()

    if status != "SUCCESS":
        print(status)
        listener.close()
        return
    
    # Server connects to this client and read the listing from the data channel
    #dataSock, _ = listener.accept()
    dataSock = listener.accept()[0]
    listing = recvMsg(dataSock).decode()
    dataSock.close()
    listener.close()

    print(listing)

# Get a file from server and bring it to ClientDir
def getCmd(ctrlSock, fileName):
    fileName = os.path.basename(fileName)
    listener, port = makeDataListener()
    sendMsg(ctrlSock, "get " + str(port) + " " + fileName)
    status = recvMsg(ctrlSock).decode()
    
    if status != "SUCCESS":
        print(status)
        listener.close()
        return
    
    dataSock, _ = listener.accept()
    fileData = recvMsg(dataSock)
    dataSock.close()
    listener.close()
    
    savePath = os.path.join("ClientDir", fileName)
    with open(savePath, "wb") as f:
        f.write(fileData)

    print("Downloaded " + fileName + " (" + str(len(fileData)) + " bytes)")

# Server connects with this client and client sends file over data channel
def putCmd(ctrlSock, fileName):
    fileName = os.path.basename(fileName)
    filePath = os.path.join("ClientDir", fileName)

    if not os.path.isfile(filePath):
        print("FAILURE File not found: " + fileName)
        return
    
    listener, port = makeDataListener()
    sendMsg(ctrlSock, "put " + str(port) + " " + fileName)
    status = recvMsg(ctrlSock).decode()

    if status != "SUCCESS":
        print(status)
        listener.close()
        return
    
    dataSock = listener.accept()[0]

    with open(filePath, "rb") as f:
        fileData = f.read()

    sendMsg(dataSock, fileData)

    dataSock.close()
    listener.close()

    print("Uploaded " + fileName + " (" + str(len(fileData)) + " bytes)")



# {=== Main Function of CLient ===}
ctrlSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ctrlSock.connect((serverName, serverPort))

while True:
    line = input("ftp> ").strip()
    if not line:
        continue
    parts = line.split(" ", 1)
    cmd = parts[0]

    if cmd == "quit":
        sendMsg(ctrlSock, "quit")
        break
    elif cmd == "ls":
        lsCmd(ctrlSock)
    elif cmd == "get" and len(parts) == 2:
        getCmd(ctrlSock, parts[1])
    elif cmd == "put" and len(parts) == 2:
        putCmd(ctrlSock, parts[1])
    else:
        print("Commands: get [file] | put [file] | ls | quit")

ctrlSock.close()