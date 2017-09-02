import socket
import thread
import sys
import pickle
import tqdm

def discovery_mode():
    disc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    disc_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        disc_socket.bind(('', 2017))
        print "In Discovery Mode"
    except socket.error as err:
        print "Error while binding discovery socket!"
        print err
    thread.start_new_thread(handle_flooding, (disc_socket,))
    return disc_socket


def handle_flooding(disc_socket):
    while True:
        text, addr = disc_socket.recvfrom(1024)
        print "Received Message {} from {}".format(text, addr)
        if text == "REMOTEFLIX_DISCOVERY_REQUEST":
            disc_socket.sendto("REMOTEFLIX_DISCOVERY_RESPONSE", addr)
            print "Discovery Process Complete!"

def get_tcp_server(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((host, port))
    except socket.error as msg:
        print "Error Binding to Host: %s on Port: %s" %(host, port)
        print msg
        sys.exit()
    print "Started TCP Server on Host: %s, Port: %s" %(host, port)
    s.listen(0)
    return s


def serve(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((host, port))
    except socket.error as msg:
        print "Error Binding to Host: %s on Port: %s" %(host, port)
        print msg
        sys.exit()
    print "Started TCP Server on Host: %s, Port: %s" %(host, port)
    s.listen(0)


    while True:
        conn, addr = s.accept()
        print "Connected with %s" %(addr[0] + " " + str(addr[1]))

        thread.start_new_thread(client_thread, (conn, ))
        #client_thread(conn)

def client_thread(conn):
    #conn.send("Welcome to RemoteFlix")
    print "Client thread begins..."
    buf = ''
    try:
        initial = conn.recv(1024)
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
                    data = conn.recv(1024)
    except Exception as e:
        print e
        print "error while receiving data"

    print "Closing connection!"
    try:
        conn.close()
    except Exception as e:
        print e

if __name__ == '__main__':
    try:
        #disc_socket = discovery_mode()
        serve('', 4000)
    except KeyboardInterrupt:
        print "Closing Discovery Socket"
        #disc_socket.close()



