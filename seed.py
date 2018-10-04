# list of peer

#!/usr/bin/env python3

import socket
import _thread
import sys

HOST = sys.argv[1]  # Standard loopback interface address (localhost) sys.argv[1]
PORT = int(sys.argv[2])  # Port to listen on (non-privileged ports are > 1023) sys.argv[2]

peers = []
connections = []

#lock = _thread.allocate_lock()

def on_new_client(conn,addr):
    
    #print("Client connected", conn, addr)
    
	while True:
		print("Waiting for somting to receive!!!", addr, " connected")
		data = conn.recv(1024)
		print(data)

		if data == b"REQUEST_PEER":
			peerInfo = []
			for ip, port in peers:
				peerInfo.append(ip)

			dataSend = '-'.join(peerInfo)
			sendData(conn, dataSend)
		else:
			print(addr[0], ":", addr[1], "Existed System!!!")
			peers.remove(addr)
			break;
		#conn.sendall(dataSend.encode('utf-8'))
	
def sendData(conn, data):
	data_send = str(len(data)) + "#" + data
	conn.sendall(data_send.encode('utf-8'))
	return

def main():

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen()
	while(1):
	    conn, addr = s.accept()
	    peers.append(addr)
	    connections.append(conn)
	    _thread.start_new_thread(on_new_client,(conn,addr))

if __name__ == '__main__':
    main()