import socket

ADDR = ('127.0.0.1', 8007)

client = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)

client.connect(ADDR)
msg = "client is connected"

def main():
    while True:
        try: 
            client.sendall(msg)
            while True:
                part = client.recv(16)
                client.shutdown(socket.SHUT_WR)
                print part
                if len(part) < 16:
                    client.close()
                    break
        except Exception as e:
            client.close()
            print e



if __name__ == '__main__':


#find setting in doc to fix port is in use > dynamically?

