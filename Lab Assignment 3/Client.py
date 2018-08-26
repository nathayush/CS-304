import os
import socket
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread

class MyEventHandler(FileSystemEventHandler):
    def __init__(self, node):
        self.client_node = node

    def on_created(self, event):
        if not event.is_directory:
            print("\nwatchdog: (created) " + event.src_path.split("/")[-1])
            self.client_node.send_option("upload")
            self.client_node.send_file(event.src_path.split("/")[-1])

    def on_modified(self, event):
        if not event.is_directory:
            print("\nwatchdog: (modified) " + event.src_path.split("/")[-1])
            self.client_node.send_option("modify")
            self.client_node.send_file(event.src_path.split("/")[-1])

    def on_deleted(self, event):
        if not event.is_directory:
            print("\nwatchdog: (deleted) " + event.src_path.split("/")[-1])
            self.client_node.send_option("delete")
            self.client_node.send_name(event.src_path.split("/")[-1])

    def on_moved(self, event):
        if not event.is_directory:
            print("\nwatchdog: (moved) " + event.src_path.split("/")[-1] + " --> " + event.dest_path.split("/")[-1])
            self.client_node.send_option("move")
            self.client_node.send_name(event.src_path.split("/")[-1])
            self.client_node.send_name(event.dest_path.split("/")[-1])

class Client():
    def __init__(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Server_IP = "127.0.1.1"
        Server_Port = 2222
        self.server_sock.connect((Server_IP, Server_Port))
        trackingfolder = "/tracking_folder"
        downloadfolder = "/download_folder"
        self.rootpath = os.getcwd()
        self.path = self.rootpath + trackingfolder
        self.download_path = self.rootpath + downloadfolder
        os.chdir(self.path)
        print("Tracking " + str(self.path))
        self.run()

    def run(self):
        option = ''
        try:
            print("\nOPTIONS: 1. Sync; 2. Download; 3. Quit")
            print("ENTER OPTION NUMBER: ")
            while option != "3":
                option = input()
                print("")
                if option == "1":
                    self.sync()
                elif option == "2":
                    self.download()
        except KeyboardInterrupt:
                self.wd.join()
        self.wd.join()

    def download(self):
        self.get_index()
        files = input("ENTER FILE NAME: ")
        self.send_name(files)

        file_size = self.server_sock.recv(32)
        file_size = int(file_size, 2)
        block = 4096
        os.chdir(self.download_path)
        print(files)
        with open(files, 'wb') as f:
            while file_size > 0:
                if file_size < block:
                    block = file_size
                data = self.server_sock.recv(block)
                f.write(data)
                file_size -= len(data)
        print("Received " + files)
        os.chdir(self.path)

    def get_index(self):
        self.send_option("index")
        size = self.server_sock.recv(16).decode()
        size = int(size, 2)
        index = []
        for i in range(0, size):
            size = self.server_sock.recv(16)
            size = int(size, 2)
            index.append(str(self.server_sock.recv(size).decode()))
        print(index)

    def sync(self):
        for files in os.listdir(self.path):
            self.send_option("upload")
            self.send_file(files)
        self.wd = Thread(target=self.wdog, args=())
        self.wd.start()

    def send_name(self, files):
        size = len(files)
        size = bin(size)[2:].zfill(16)
        self.server_sock.send(size.encode())
        self.server_sock.send(files.encode())

    def send_option(self, files):
        size = len(files)
        size = bin(size)[2:].zfill(16)
        self.server_sock.send(size.encode())
        self.server_sock.send(files.encode())

    def send_file(self, files):
        print("Sending " + files)
        self.send_name(files)

        file_path = os.path.join(self.path,files)
        file_size = os.path.getsize(file_path)
        file_size = bin(file_size)[2:].zfill(32)
        self.server_sock.send(file_size.encode())
        with open(files, "rb") as f:
            data = f.read()
            self.server_sock.sendall(data)
        print("Sent.")

    def wdog(self):
        event_handler = MyEventHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.path)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
                observer.stop()
                observer.join()

client_node = Client()
