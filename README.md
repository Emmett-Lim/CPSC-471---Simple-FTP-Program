# CPSC471 Programming Assignment 1 - Simple FTP
[ Names / emails ]
- Emmett Lim - emmettklim@csu.fullerton.edu

[ Language ] 
- Python

## How to run
1. Place a text file in either ClientDir or ServerDir or even both (Make sure to add text inside the text file!).
2. Start the server:
```bash
python server.py [port] #e.g. python server.py 1234
```
3. Start the client:
```bash
python client.py [server] [port] #e.g. python client.py localhost 1234
```
4. At the ftp> prompt:  ls | get [file] | put [file] | quit

> [!NOTE]
> - Depending on how you downloaded python onto your OS, you use either python, python3, or py to run the script files.
> - Server handles one client at a time.
> - Files go between ServerDir and ClientDir

## Protocol Design
Framing (used on both channels): every message is [10 bytes data length,] [data]

The receiver reads exactly 10 bytes, parses the length, then loops on
recv() until that many bytes arrive. Senders loop on send() until all
bytes are sent. This handles partial sends/receives and large files.

Control channel (client's first connection; lasts the whole session)

Client -> Server (text):
- "ls <dataPort>"<br>
- "get <dataPort> [filename]"<br>
- "put <dataPort> [filename]"<br>
- "quit"<br>

Server -> Client (text, one reply per ls/get/put):<br>
- "SUCCESS"
- "FAILURE [reason]"

Data channel (one per ls/get/put; closed after the transfer)
  1. Client binds a listening socket to port 0 (ephemeral port).
  2. Client sends the command with that port on the control channel.
  3. Server replies SUCCESS/FAILURE on the control channel.
      - On FAILURE no data channel is opened; client closes its listener.
      - On SUCCESS the server connects to the client's port.
  4. One framed message carries the data: file contents (get: server->
     client, put: client->server) or the listing (ls: server->client).
  5. Sender closes the data socket; client closes its listener.

## Examples
1. This gets text file "servertest.txt" from ServerDir and puts it into ClientDir
```bash
get servertest.txt
```

2. This puts text file "clienttest.txt" from ClientDir to ServerDir
```bash
put clienttest.txt
```
