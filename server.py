import socket
import threading
from crypto import Crypto
import base64

PORT = 4720
SERVER = socket.gethostbyname(socket.gethostname())
SERVER = 'localhost'
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"
crypto = Crypto()

# danh sách socket, name2addr là 1 dict trả về tên khi nhập vào addr, adrr2name tương tự
clients, name2addr, addr2name = [], {}, {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)
shared_key = []
online = ''

def startChat():
	print(f"server đang đợi ở {SERVER}:{PORT}")
	server.listen()
	online = '1'
	while True:
		conn, addr = server.accept()

		private_key = crypto.generate_private_key()
		peer_public_key = private_key.public_key()

		conn.send(crypto.to_bytes(peer_public_key))
		client_public_key = conn.recv(1024)
		
		client_public_key = crypto.load_public_key(client_public_key)
		shared_key.append(crypto.exchange_key(private_key, client_public_key))

		name = conn.recv(1024).decode(FORMAT)

		name2addr[name] = addr[0]
		addr2name[addr[0]] = name
		online = online + name + " "
		clients.append(conn)

		print(f"Name is :{name}")

		broadcast(f"0{name}".encode(FORMAT), conn)
		conn.send(online.encode(FORMAT))

		thread = threading.Thread(target=handle, args=(conn, addr))
		thread.start()

def handle(conn, addr):
	print(f"new connection {addr}")
	connected = True

	flag = 0
	while connected:
		try:
			message = conn.recv(1024)
			message = crypto._decrypt(message, shared_key[clients.index(conn)])
			broadcast(message)
		except:
			if flag == 0:
				remove(conn)
				print(addr2name[addr[0]], 'đã ngắt kết nối')
				broadcast('2'+ addr2name[addr[0]], None)
				flag = 1
				continue

	conn.close()

def broadcast(message, client=None):
	for c in clients:
		if c != client:
			c.send(message.encode(FORMAT) if isinstance(message, str) else message)

def remove(conn):
	if conn in clients:
		shared_key.remove(shared_key[clients.index(conn)])
		clients.remove(conn)

startChat()