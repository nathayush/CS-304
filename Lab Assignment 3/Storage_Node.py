import socket
from threading import Thread
import os

class Storage_Node(Thread):
    def __init__(self, file_type, port):
        Thread.__init__(self)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = port
        self.TYPE = file_type
        print("\t" + self.TYPE + " - " + str(self.PORT))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.IP, self.PORT))
        path = os.getcwd()
        self.path = str(path + "/storage/" + self.TYPE)
        thread = Thread(target=self.run, args=())
        thread.start()

    def upload(self):
        size = self.conn.recv(16)
        file_name = self.conn.recv(int(size, 2)).decode()

        file_size = self.conn.recv(32)
        file_size = int(file_size, 2)
        block = 4096
        with open(os.path.join(self.path, file_name), 'wb') as f:
            while file_size > 0:
                if file_size < block:
                    block = file_size
                data = self.conn.recv(block)
                f.write(data)
                file_size -= len(data)
        print("\nReceived " + file_name)

    def modify(self):
        size = self.conn.recv(16)
        file_name = self.conn.recv(int(size, 2)).decode()

        file_size = self.conn.recv(32)
        file_size = int(file_size, 2)
        block = 4096
        with open(os.path.join(self.path, file_name), 'wb') as f:
            while file_size > 0:
                if file_size < block:
                    block = file_size
                data = self.conn.recv(block)
                f.write(data)
                file_size -= len(data)
        print("Modified " + file_name)

    def delete(self):
        size = self.conn.recv(16)
        file_name = self.conn.recv(int(size, 2)).decode()
        os.remove(os.path.join(self.path, file_name))
        print("\nDeleted " + file_name)

    def move(self):
        size = self.conn.recv(16)
        file_name = self.conn.recv(int(size, 2)).decode()

        size2 = self.conn.recv(16)
        file_name2 = self.conn.recv(int(size, 2)).decode()

        os.rename(os.path.join(self.path, file_name), os.path.join(self.path, file_name2))
        print("Moved " + file_name + " --> " + file_name2)

    def download(self):
        size = self.conn.recv(16)
        size = int(size, 2)
        file_name = self.conn.recv(size).decode()
        print("\nDownload request for " + file_name)

        file_size = os.path.getsize(os.path.join(self.path, file_name))
        file_size = bin(file_size)[2:].zfill(32)
        self.conn.send(file_size.encode())
        with open(os.path.join(self.path, file_name), "rb") as f:
            data = f.read()
            self.conn.sendall(data)
        print("\nSent.")

    def run(self):
        self.sock.listen(1)
        (self.conn, add) = self.sock.accept()
        print(self.TYPE + "_node connected to server " + str(add[0]) + ":" + str(add[1]))

        while True:
            while True:
                option_size = self.conn.recv(16)
                if not option_size:
                    break
                option = self.conn.recv(int(option_size, 2)).decode()
                if option == "upload":
                    self.upload()
                elif option == "modify":
                    self.modify()
                elif option == "delete":
                    self.delete()
                elif option == "move":
                    self.move()
                elif option == "download":
                    self.download()


print("Storage IP: " + str(socket.gethostbyname(socket.gethostname())))
print("Ports:")
txt_node = Storage_Node("txt", 1234)
pdf_node = Storage_Node("pdf", 2345)
mp3_node = Storage_Node("mp3", 3456)
other_node = Storage_Node("other", 4567)
