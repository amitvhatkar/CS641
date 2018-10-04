#!/usr/bin/env python3
import sys
import hashlib
#hashlib.sha224(b"Nobody inspects the spammish repetition").hexdigest()
import random
import socket
import _thread
import time
import datetime




temp_port_list = [17000, 18000, 16000, 19000, 20000, 21000]

PORT = int(sys.argv[2])
HOST = sys.argv[1]
PEER_PORT = 20000

N = 10
seed_threshold = 3
peers_list = []
peers_ip_list = []

file_name = "coin_info_at_"+HOST+"_"+str(PORT)+".txt"
node_file = open(file_name,"w+")

peers_set = set()

sys.stdout = open('client_out_'+file_name, 'w')

no_of_seeds_connectd = 0
connected_nodes = []

sha_msg = set()
lock = _thread.allocate_lock()


seeds = [
	
	{
		'IP': '10.196.27.113',
		'PORT' : 15000,
		'IsSeed' : True,
		'Connected' : False	
	},
	{
		'IP': '10.130.155.41',
		'PORT' : 15000,
		'IsSeed' : True,
		'Connected' : False
	},
	{
		'IP': '127.0.0.1',
		'PORT' : 15004,
		'IsSeed' : True,
		'Connected' : False
	},
	{
		'IP': '127.0.0.1',
		'PORT' : 15005,
		'IsSeed' : True,
		'Connected' : False
	},
	{
		'IP': '127.0.0.1',
		'PORT' : 15006,
		'IsSeed' : True,
		'Connected' : False
	}
]


#HOST.append('127.0.0.1')  # The server's hostname or IP address: 
#PORT.append(65432)        # The port used by the server


def connectToNodes(node_list, is_to_seed = False):

	global no_of_seeds_connectd, connected_nodes
	#print(len(seeds))
	for node in node_list:

		if not node['Connected']:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
			#print(node['IP'], node['PORT'],(node['IP'], node['PORT']), '\n')
			try:
				s.connect((node['IP'], node['PORT']))			
			except:
				print("Error connecting: ",(node['IP'], node['PORT']))
				#node['socket'] = None
				#node['Connected'] = False
				#connected_nodes.append(node)
				continue

			if is_to_seed:
				no_of_seeds_connectd = no_of_seeds_connectd + 1
				if(no_of_seeds_connectd == seed_threshold):
					break;

			node['socket'] = s;
			node['Connected'] = True
			connected_nodes.append(node)
			if not is_to_seed:
				_thread.start_new_thread(peer_processing,(node,))
			print("Connected sucessfully ",(node['IP'], node['PORT']))
		#s.close()
	#print(connected_nodes)


def learnAboutPeers():
	global no_of_seeds_connectd, connected_nodes, peers_list, peers_set
	#peers_set = set()
	for node in connected_nodes:
		if node['IsSeed'] :
			node['socket'].send(b"REQUEST_PEER")
			data = node['socket'].recv(1024)
			data = data.decode("utf-8")
			dataLen = int(data.split("#")[0])
			data = data.split("#")[1]
			#print(dataLen, len(data))
			while(len(data) < dataLen):
				data = data + node['socket'].recv(1024)

			print(set(data.split("-")))
			peers_set = peers_set | set(data.split("-"))
			
	#print(peers_set, "Received from server !!")
	i = 0;

	for peer in peers_set:
		
		node = {
			'IP': peer,
			'PORT' : PEER_PORT,
			'IsSeed' : False,
			'Connected' : False			
		}
		print(peer, "*******", node not in peers_list)
		if peer not in peers_ip_list:
			print("Set of peers: ", peers_set, peers_list)
			#node['Connected'] = False
			peers_list.append(node)
			peers_ip_list.append(peer)
		#i = i + 1
		#print("Node added : ", node)

		'''
		BUG here
		'''

		

	#print(peers_list)
		

def peer_processing(node):
		
	global sha_msg

	conn = node['socket']
	addr = (node['IP'], node['PORT'])
	while True:
		#print("waiting to receive !!!!")
		data = conn.recv(1024)
		if data:
			#print("broad casted Info received", addr)

			lock.acquire()

			data = data.decode('utf-8')
			#print("\n???????????????\n", data, "\n?????????????????\n")
			data_len = int(data.split("#")[0])
			data = data.split("#")[1]
			#print(data_len, "----------", len(data))
			while data_len > len(data):
				data = data + conn.recv(1024).decode('utf-8')
			data_hash = hashlib.sha224(data.encode('utf-8')).hexdigest()
			if data_hash not in sha_msg:
				sha_msg.add(data_hash)
				data_to_file = "RECEIVED FROM " + addr[0] + " " + str(addr[1])+ "::" +data
				node_file.write(data_to_file)
				node_file.flush()
				#print("Passing to toher nodes----------\n")
				pass_to_other_nodes(data)

			lock.release()
		else:
			connected_nodes.remove(node)
			peers_set.erase(node['IP'])
			peers_list.remove(node['IP'])
			peers_ip_list.remove(node['IP'])

			print(addr[0], ":", addr[1], "Existed System!!!")
			_thread.exit()
			break;

def pass_to_other_nodes(data):
	print("Sending data:", data)
	for node in connected_nodes:
		if not node['IsSeed'] and node['Connected']:
			#print("\t\t\a",node['IP'],"-------", node['PORT'])
			sendData(node['socket'], data)

def sendData(conn, data):
	data_send = str(len(data)) + "#" + data
	try:
		conn.sendall(data_send.encode('utf-8'))
	except:
		print("Error in sending")
	return

def create_socket(port):
	global connected_nodes
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen()
	print("Started accepting")
	while(1):

		conn, addr = s.accept()
	    #peers.append(addr)
	    #connections.append(conn)

		node = {
			'IP': addr[0],
			'PORT' : int(addr[1]),
			'IsSeed' : False,
			'Connected' : True,
			'socket' : conn
		}
		connected_nodes.append(node)
		_thread.start_new_thread(peer_processing,(node,))


def broadcast_message():
	global sha_msg
	while True:
		random_no = random.randint(0,len(peers_list) - 1)

		print("Generated random no : ", random_no, " length of peers: ", len(peers_list))

		lock.acquire()

		node = peers_list[random_no]
		time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		message = time_stamp +" : "+HOST+":"+str(PORT)+" pays "+str(N)+" BTC to "+node["IP"]+":"+str(node['PORT'])+"\n"
		#print("Writing to file.....")
		data_hash = hashlib.sha224(message.encode('utf-8')).hexdigest()
		if data_hash not in sha_msg:
			sha_msg.add(data_hash)
			node_file.write(message)
			node_file.flush()
			pass_to_other_nodes(message)
		
		lock.release()
		time.sleep(6)


#def receive_broadcasted_msg():


def main():
	global seeds,peers_list, sha_msg

	_thread.start_new_thread(create_socket,(sys.argv[1],))#create_socket(sys.argv[1])
	#_thread.start_new_thread(broadcast_message,())
	#_thread.start_new_thread(receive_broadcasted_msg,())

	while True:
		print("Checking for seeds")
		connectToNodes(seeds, is_to_seed = True) # seeds
		learnAboutPeers()
		print("Checking for peers", len(peers_list))
		connectToNodes(peers_list, is_to_seed = False) #peers
		_thread.start_new_thread(broadcast_message,())
		#print(connected_nodes)
		

		print("Printing sha msg\n",len(sha_msg), "End\n")

		#node_file.write("\n\n\n\n\n")
		#node_file.flush()
		
		time.sleep(10)

		print("After 6 seconds......")

if __name__ == '__main__':
    main()