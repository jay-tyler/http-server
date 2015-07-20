import socket

ADDR = ('127.0.0.1', 8004)

client = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)

client.connect(ADDR)
msg = "hello"

try: 
    client.sendall(msg)
    while True:
        part = client.recv(16)
        client.shutdown(socket.SHUT_WR)
        print part
        if len(part) < 16:
            print 'message recived'
            # client.close()
            # break
except Exception as e:
    client.close()
    print e
    print 'did not close'
