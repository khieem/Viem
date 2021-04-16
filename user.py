import socket

PORT = 4720
SERVER = "192.168.32.129"
ADDRESS = (SERVER, PORT)
FORMAT = 'utf8'

class User:
    def __init__(self):
        self.name = ''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_ip(self):
        return self.socket.gethostbyname(self.socket.gethostname())

    def connect(self):
        self.socket.connect(ADDRESS)

