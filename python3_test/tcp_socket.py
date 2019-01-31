import socket
import selectors 
import sys
import signal

def read_data(sock,mask):
    data = sock.recv(1000)
    if not data:
        print("read data error\n")
        sel.unregister(sock)
        return 
    received = len(data)
    print('%d bytes received,%s'%(received,data))



def send_data(fd,mask):
    data = fd.readline()

    data = data.strip()
    #print(data)
    if data:
        print("send data")
        sock.sendall(data.encode())
    else:
        print("read data error\n")
        sys.exit()

def exit(signal_num,frame):
    sock.close()
    sys.exit()

signal.signal(signal.SIGINT,exit)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(True)
sock.connect(('203.195.244.181',7000))
#sock.connect(('127.0.0.1',1234))
#sock.connect(('129.28.32.34',6800))
sel = selectors.DefaultSelector()
fd = sys.stdin
sel.register(fd,selectors.EVENT_READ,send_data)
sel.register(sock,selectors.EVENT_READ,read_data)
while True:
    events = sel.select()
    for key,mask in events:
        callback = key.data
        callback(key.fileobj,mask)

