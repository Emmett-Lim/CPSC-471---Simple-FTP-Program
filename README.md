# CPSC471 Programming Assignment 1 - Simple FTP
[ Names / emails ]
- Emmett Lim - emmettklim@csu.fullerton.edu

[ Language ] 
- Python

## How to run
1. Start the server (in the folder whose files you want to serve):
       python serv.py <PORT>          e.g.  python serv.py 1234
2. Start the client (ideally from a different folder):
       python cli.py <server> <PORT>  e.g.  python cli.py localhost 1234
3. At the ftp> prompt:  ls | get <file> | put <file> | quit

### Notes
- Depending on how you donwloaded python onto your OS, you use either python, python3, or py to run the script files.
- Server handles one client at a time.
- Files are transferred in binary mode, so any file type works.
- Files go to/from the current directory of the server and client.

## PROTOCOL DESIGN
Framing (used on both channels): every message is [10 ASCII bytes: data length, zero-padded] [data]

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
     On FAILURE no data channel is opened; client closes its listener.
  4. On SUCCESS the server connects to the client's port.
  5. One framed message carries the data: file contents (get: server->
     client, put: client->server) or the listing (ls: server->client).
  6. Sender closes the data socket; client closes its listener.

[ Examples ]
