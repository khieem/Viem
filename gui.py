import re
import threading
import os
from typing import ForwardRef
from crypto import Crypto
from tkinter import *
from tkinter import filedialog
from PIL import Image,ImageTk
from os.path import dirname, abspath

GRAY = '#f5f5f5'
ORANGE_FG = '#ff5722'
ORANGE_BG = '#ff8a65'
crypto = Crypto()

class GUI:

	def __init__(self, client):
		self.client = client
		self.Window = Tk()
		self.Window.withdraw()

		self.login = Toplevel()
		self.login.title("Viêm")
		self.login.configure(bg='white')
		sw = self.login.winfo_screenwidth()
		sh = self.login.winfo_screenheight()
		w, h = 250, 300
		self.login.geometry('%dx%d+%d+%d' % (w, h, (sw-w)/2, (sh-h)/2))
		
		# self.chat_history = open('ls', 'a')
		self.pls = Label(self.login, text='Chào bạn', font='Segoe 14 bold', bg='white', bd=0)
		self.pls.place(rely=0.1, relwidth = 1)

		self.entryName = Entry(self.login, font="Segoe 14", bg=GRAY, bd=0)
		self.entryName.insert(END, 'tên')
		self.entryName.place(relwidth=.7, relheight=0.12, relx=0.15, rely=0.30)
		self.friend_list = {}
		self.images = []

		self.default_name = True
		self.default_pwd = True
		self.entryName.bind("<Button-1>", self.delete_name)
		self.entryName.bind("<Tab>", self.delete_pwd)

		self.entry_pwd = Entry(self.login, font="Segoe 14", bg=GRAY, bd=0)
		self.entry_pwd.insert(END, 'mật khẩu')
		self.entry_pwd.place(relwidth=.7, relheight=0.12, relx=0.15, rely=0.45)
		self.entry_pwd.bind("<Button-1>", self.delete_pwd)

		name = self.entryName.get().strip()
		self.go = Button(self.login,
						text="Đăng nhập",
						bg=ORANGE_FG,
						fg='white',
						font="Segoe 14 bold",
						borderwidth=0,
						command=lambda:self.goAhead(self.entryName.get().strip(), self.entry_pwd.get()))
						
		self.go.place(relwidth=.7, relheight=0.12, relx=0.15, rely=0.60)
		self.Window.mainloop()

	def delete_name(self, event):
		if self.default_name:
			self.entryName.delete(0, END)
			self.default_name = False

	def delete_pwd(self, event):
		if self.default_pwd:
			self.entry_pwd.delete(0, END)
			self.default_pwd = False

	def goAhead(self, name, pwd):
		if name == '':
			return
		self.login.destroy()
		self.layout(name)
		self.client.set_name(name)
		self.pwd = pwd
		rcv = threading.Thread(target=self.receive)
		rcv.start()

	def stop(self):
		os._exit(0)

	def select_file(self, event):
		fp = filedialog.askopenfilename()
		if fp[-4:] == '.jpg':
			img = Image.open(fp).resize((300, 400), Image.ANTIALIAS)
			self.images.append(ImageTk.PhotoImage(img))
			self.sendButton('3 ' +self.name + ' ' +fp)
		else:
			self.sendButton('4 '+ self.name + ' ' +fp)

	def layout(self, name):
		self.name = name
		self.Window.deiconify()
		self.Window.protocol("WM_DELETE_WINDOW", self.stop)
		self.Window.title("Viêm")
		self.Window.resizable(width=False, height=False)
		self.Window.configure(width=800, height=600, bg="white")
		self.Window.geometry('%dx%d+%d+%d' % (800, 600, 50, 50))
		
		self.friends = Frame(self.Window, background=ORANGE_BG, borderwidth=1)
		self.friends.place(relwidth=0.3, relheight=1)
		self.chat_zone = Label(self.Window, background='white', borderwidth=0)
		self.chat_zone.place(relwidth=0.7, relx=0.3, relheight=1)
		self.chao = Label(self.friends, text=f'Chào {self.name}', font='Segoe 20', background=ORANGE_BG)
		self.chao.pack(fill='x', side=TOP, pady=24)

		self.f1 = False
		self.cho_hien_thi_tin_nhan = Text(self.chat_zone, bg='white', fg="BLACK", font="Segoe 14", borderwidth=0)
		self.cho_hien_thi_tin_nhan.place(relheight=0.9, relx=0, rely=0)
		self.cho_hien_thi_tin_nhan.config(state=DISABLED)

		self.entryMsg = Entry(self.chat_zone, bg=GRAY, fg="black", font="Segoe 14", borderwidth=0)
		self.buttonMsg = Button(self.chat_zone,
										text="Gửi",
										font="Segoe 10 bold",
										bg=ORANGE_FG,
										fg="white",
										borderwidth=0,
										command=lambda: self.sendButton(f'{self.name}: {self.entryMsg.get()}'))
		self.buttonMsg.bind('<Button-3>', self.select_file)
	
		scrollbar = Scrollbar(self.cho_hien_thi_tin_nhan)
		scrollbar.place(relheight=1, relx=0.974)
		scrollbar.config(command=self.cho_hien_thi_tin_nhan.yview)

	def sendMessage(self, mode=None):
		self.cho_hien_thi_tin_nhan.config(state=DISABLED)
		while True:
			message = self.msg
			self.client.send(message)
			break

	def sendButton(self, msg, mode=None):
		self.cho_hien_thi_tin_nhan.config(state=DISABLED)
		self.msg = crypto._encrypt(msg, self.shared_key)
		self.entryMsg.delete(0, END)
		snd = threading.Thread(target=self.sendMessage)
		snd.start()

	def new_friend_button(self, name):
		f = Button(self.friends, text=name, height=3, background='white', font='Segoe 11', borderwidth=0, command=lambda:self.select())
		f.pack(side=TOP, fill='x', pady=1)
		return f
	
	def select(self):
		if self.f1 == False:
			self.entryMsg.place(relwidth=0.84, relheight=0.07, relx=0.01, rely=0.915)
			self.entryMsg.focus()
			self.buttonMsg.place(relx=0.87, relheight=0.07, relwidth=0.11, rely=0.915)
			self.f1 = True

	def write_chat_history(self, message):
		self.chat_history.write(message+'\n')

	def receive(self):
		while True:
			try:
				message = self.client.receive()
				if message[0] == '-': # yêu cầu trao đổi khoá
					server_public_key = message.encode()
					private_key = crypto.generate_private_key()
					peer_public_key = private_key.public_key()
					self.client.socket.send(crypto.to_bytes(peer_public_key))
					server_public_key = crypto.load_public_key(server_public_key)
					self.shared_key = crypto.exchange_key(private_key, server_public_key)
					self.client.send(self.client.get_name())			
				elif message[0] == '0': # báo người moi trực tuyến cho nguoi dang chay
					self.friend_list[message[1:]] = self.new_friend_button(message[1:])
				elif message[0] == '1': # danh sahc nhung nguoi truc tuyen cho nguoi moi khoi dong
					for t in message[1:].split():
						if t != self.name:
							self.friend_list[t] = self.new_friend_button(t)
				elif message[0] == '2': # bao nguoi da thoat
					self.friend_list[message[1:]].destroy()
				elif message[0] == '3':
					fp = message[1:]
					m = fp.split()
					s, fp = m
					img = Image.open(fp).resize((300, 400), Image.ANTIALIAS)
					self.images.append(ImageTk.PhotoImage(img))
					self.cho_hien_thi_tin_nhan.config(state=NORMAL)
					self.cho_hien_thi_tin_nhan.insert(END, s +':\n')
					self.cho_hien_thi_tin_nhan.image_create(END,image=self.images[-1])
					self.cho_hien_thi_tin_nhan.insert(END, '\n\n')
					self.cho_hien_thi_tin_nhan.config(state=DISABLED)
				elif message[0] == '4':
					fp = message[1:].split()
					s, f = fp
					d = dirname(abspath(__file__))
					os.system('copy '+f.replace('/', '\\')+' '+d)
					os.system('copy ls+')
					os.system('copy '+ os.getcwd()+'\\ls'+' '+d)
					pat = r'\w+\.(.+)$'
					f = re.search(pat, f).group()
					self.cho_hien_thi_tin_nhan.config(state=NORMAL)
					self.cho_hien_thi_tin_nhan.insert(END, s + ' gửi ' +f + "\n\n")
					self.cho_hien_thi_tin_nhan.config(state=DISABLED)		
				else:
					self.cho_hien_thi_tin_nhan.config(state=NORMAL)					
					self.cho_hien_thi_tin_nhan.insert(END, message + "\n\n")
					self.cho_hien_thi_tin_nhan.config(state=DISABLED)
					self.cho_hien_thi_tin_nhan.see(END)
			except:
				print("có gì đó sai sai :(")
				self.client.socket.close()
				break

