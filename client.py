from gui import *
from user import *

client = User()
client.connect()

g = GUI(client)
