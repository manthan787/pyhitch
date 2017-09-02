from __future__ import division
from Tkinter import Tk, Frame, E, W, S, N
import Tkinter as tk
import ttk
from tkFileDialog import askopenfilename
from DiscoveryServiceServer import get_ip_address, get_server
from config import (DISCOVERY_SERVICE_PORT, DISCOVERY_SERVICE_TYPE,\
                    DISCOVERY_SERVICE_NAME)
from DiscoveryServiceClient import MyListener
from zeroconf import Zeroconf, ServiceBrowser
import socket
from server import get_tcp_server
import thread
import os
import pickle
import tqdm

ip = get_ip_address()
zconf = get_server(DISCOVERY_SERVICE_TYPE, DISCOVERY_SERVICE_NAME, ip,
                    DISCOVERY_SERVICE_PORT)


browser_zconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(browser_zconf, DISCOVERY_SERVICE_TYPE, listener)


class DeviceList(object):

    def __init__(self, parent):
        self.list = ttk.Treeview(parent)
        self.device_ip_map = {}
        self.initUI()

    def initUI(self):
        self.list.heading("#0", text="Nearby Devices")
        self.list.grid(row=2, columnspan=2, sticky=W+E, padx=5, pady=5)

    def populate_list(self, services):
       self.list.delete(*self.list.get_children())
       self.device_ip_map.clear()
       for i, kv in enumerate(services.iteritems()):
            device, s = kv
            self.device_ip_map[device] = \
            socket.inet_ntoa(s.address)
            self.list.insert("", i, text=device)

    def selected_device(self):
        selected = self.list.focus()
        device_name = self.list.item(selected)['text'].strip()
        return device_name, self.device_ip_map[device_name]

    def pack(self):
        self.list.pack()


class MainApplication(Frame):

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.list = DeviceList(self)
        self.browse_button = ttk.Button(self, text="Browse",
                command=self.openfile)
        self.filename_entry = ttk.Entry(self)
        self.progressbar = ttk.Progressbar(self, orient=tk.HORIZONTAL,
        mode="determinate")
        self.filename = ""
        self.initUI()

    def initUI(self):
        self.master.title("Hitch")
        #style = ttk.Style()
        #style.theme_use("default")
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        browse_label = ttk.Label(self, text = "Select a file")
        browse_label.grid(row=0, sticky=tk.W, pady=4, padx=5)
        self.filename_entry.grid(row=1, columnspan=2, sticky=W+E+N+S, padx=5)
        self.browse_button.grid(row=1, column=2, sticky=W, padx=4)

        send = ttk.Button(self, text="Send", command=self.send_file)
        send.grid(row=2, column=2, sticky=N, pady=10)

        refresh = ttk.Button(self, text="Refresh",
                command=self.refresh)
        refresh.grid(row=2, column=2, sticky=S, pady=10)

        self.progressbar.grid(row=3, columnspan=2, rowspan=2, sticky=N+S+W+E, padx=5,
                pady=10)

    def openfile(self):
        self.filename = askopenfilename()
        self.set_text(self.filename_entry, self.filename)
        print self.filename

    def set_text(self, entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def send_file(self):
        self.progressbar['value'] = 0
        device, ip = self.list.selected_device()
        print "Sending file {} to {} at {}".format(self.filename, device, ip)
        file = self.filename
        if not os.path.isfile(file):
            raise Exception("Not a file, please provide a path to a file")
        print ip
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, 4000))
        size = os.path.getsize(file)
        meta = {"filename":os.path.basename(file), "size": size}
        meta = pickle.dumps(meta)
        init_string = "{}<ENDMETA>".format(meta)
        s.send(init_string)
        # send size to the server/receiver
        try:
            with open(file, "r") as f:
                content = f.read(1024)
                while True:
                    self.progressbar['value'] = self.progressbar['value'] +\
                    100*(len(content) / size)
                    print self.progressbar['value']
                    self.progressbar.update_idletasks()
                    if not content:
                        print "No Content in between!"
                        break
                    s.send(content)
                    content = f.read(1024)
        except Exception as e:
            print "Exception while sending file"
            print e
        finally:
            print "Closing connection!"
            s.close()


    def refresh(self):
        print listener.services
        self.list.populate_list(listener.services)

def client_thread(conn, uipbar):
    #conn.send("Welcome to RemoteFlix")
    print "Client thread begins..."
    try:
        initial = conn.recv(1024)
        print initial
        meta, file_cont = initial.split("<ENDMETA>")
        meta = pickle.loads(meta)
        print meta
        # Start receiving file content
        received = file_cont
        data = conn.recv(1024)
        with tqdm.tqdm(total=meta['size'], unit="B", unit_scale=True) as pbar:
            with open(meta['filename'], "wb") as f:
                while data:
                    if not data:
                        break
                    f.write(data)
                    pbar.update(len(data))
                    uipbar['value'] = uipbar['value'] + 100*(len(data) /
                    meta['size'])
                    uipbar.update_idletasks()
                    data = conn.recv(1024)
    except Exception as e:
        print e
        print "error while receiving data"
    finally:
        print "Closing connection!"
        try:
            conn.close()
        except Exception as e:
            print e


def serve_tcp(tcp_server_socket, uipbar):
    try:
        conn, addr = tcp_server_socket.accept()
        print "Connected with {}".format(addr)
        thread.start_new_thread(client_thread, (conn, uipbar))
    except Exception as e:
        print e


if __name__ == '__main__':
    try:
        root = Tk()
        root.geometry("600x400+300+50")
        root.configure(background='black')
        main = MainApplication(root)
        main.pack(side="top", fill="both", expand=True)
        tcp_server_socket = get_tcp_server('', 4000)
        thread.start_new_thread(serve_tcp,
                (tcp_server_socket, main.progressbar))
        root.mainloop()
        print "After mainloop"
    finally:
        print "Tearing servers down"
        zconf.unregister_all_services()
        zconf.close()
