import socket

class Server():
    def __init__(self, storage_IP):
        self.Server_IP = socket.gethostbyname(socket.gethostname())
        self.Server_PORT = 2222
        print("Server IP: " + self.Server_IP)
        print("Server port: " + str(self.Server_PORT))
        self.index = {}
        self.connect(storage_IP)

    def connect(self, storage_IP):
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_sock.bind((self.Server_IP, self.Server_PORT))

        self.txt_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.txt_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.txt_sock.connect((storage_IP, 1234))
        self.pdf_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pdf_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.pdf_sock.connect((storage_IP, 2345))
        self.mp3_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mp3_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.mp3_sock.connect((storage_IP, 3456))
        self.other_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.other_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.other_sock.connect((storage_IP, 4567))
        print("Connected to storage nodes.")
        self.storage = {"txt": self.txt_sock, "pdf": self.pdf_sock, "mp3": self.mp3_sock, "other": self.other_sock}

        print("Server is listening..." )
        # connect to client
        self.client_sock.listen(1)
        (self.conn, add) = self.client_sock.accept()
        print("Connection established with client at " + str(add[0]) + ":" + str(add[1]) + "\n")

        self.run()

    def send_option(self, server_sock, files):
        size = len(files)
        size = bin(size)[2:].zfill(16)
        server_sock.send(size.encode())
        server_sock.send(files.encode())

    def upload(self):
        size = self.conn.recv(16)
        file_name = self.conn.recv(int(size, 2)).decode()

        file_type = file_name[file_name.index('.')+1:]
        if file_type != "txt" and file_type != "pdf" and file_type != "mp3":
            file_type = "other"

        self.send_option(self.storage[file_type], "upload")
        self.storage[file_type].send(size)
        self.storage[file_type].send(file_name.encode())

        self.index[file_name] = self.storage[file_type]

        file_size = self.conn.recv(32)
        self.storage[file_type].send(file_size)
        file_size = int(file_size, 2)
        block = 4096
        while file_size > 0:
            if file_size < block:
                block = file_size
            data = self.conn.recv(block)
            self.storage[file_type].send(data)
            file_size -= len(data)
        print("\nReceived " + file_name)

    def download(self):
        size = self.conn.recv(16)
        int_size = int(size, 2)
        file_name = self.conn.recv(int_size).decode()

        print("\nDownload request for " + file_name)

        file_type = file_name[file_name.index('.')+1:]
        if file_type != "txt" and file_type != "pdf" and file_type != "mp3":
            file_type = "other"

        self.send_option(self.storage[file_type], "download")

        self.storage[file_type].send(size)
        self.storage[file_type].send(file_name.encode())

        file_size = self.storage[file_type].recv(32)
        self.conn.send(file_size)
        file_size = int(file_size, 2)
        block = 4096
        while file_size > 0:
            if file_size < block:
                block = file_size
            data = self.storage[file_type].recv(block)
            self.conn.send(data)
            file_size -= block
        print("Sent.")

    def modify(self):
        size = self.conn.recv(16)
        file_name = self.conn.recv(int(size, 2)).decode()

        file_type = file_name[file_name.index('.')+1:]
        if file_type != "txt" and file_type != "pdf" and file_type != "mp3":
            file_type = "other"

        self.send_option(self.storage[file_type], "modify")
        self.storage[file_type].send(size)
        self.storage[file_type].send(file_name.encode())

        file_size = self.conn.recv(32)
        self.storage[file_type].send(file_size)
        file_size = int(file_size, 2)
        block = 4096
        while file_size > 0:
            if file_size < block:
                block = file_size
            data = self.conn.recv(block)
            self.storage[file_type].send(data)
            file_size -= len(data)
        print("\nModified " + file_name)

    def delete(self):
        size = self.conn.recv(16)
        file_name = self.conn.recv(int(size, 2)).decode()

        file_type = file_name[file_name.index('.')+1:]
        if file_type != "txt" and file_type != "pdf" and file_type != "mp3":
            file_type = "other"

        self.send_option(self.storage[file_type], "delete")
        self.storage[file_type].send(size)
        self.storage[file_type].send(file_name.encode())

        del self.index[file_name]
        print("\nDeleted " + file_name)

    def move(self):
        size = self.conn.recv(16)
        file_name = self.conn.recv(int(size, 2)).decode()

        file_type = file_name[file_name.index('.')+1:]
        if file_type != "txt" and file_type != "pdf" and file_type != "mp3":
            file_type = "other"

        self.send_option(self.storage[file_type], "move")
        self.storage[file_type].send(size)
        self.storage[file_type].send(file_name.encode())

        size2 = self.conn.recv(16)
        file_name2 = self.conn.recv(int(size, 2)).decode()
        self.storage[file_type].send(size2)
        self.storage[file_type].send(file_name2.encode())

        del self.index[file_name]
        self.index[file_name2] = self.storage[file_type]
        print("\nMoved " + file_name + " --> " + file_name2)

    def get_index(self):
        lst = self.index.keys()
        self.conn.send(bin(len(lst))[2:].zfill(16).encode())

        for files in lst:
            size = len(files)
            size = bin(size)[2:].zfill(16)
            self.conn.send(size.encode())
            self.conn.send(files.encode())

        self.download()




    def run(self):
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
            elif option == "index":
                self.get_index()
            elif option == "download":
                self.download()


server_node = Server("127.0.1.1")
