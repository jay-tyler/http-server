import socket

ADDR = ('127.0.0.1', 8011) #port 0 may force os to find an open port

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
            print msg
            break



if __name__ == '__main__':
    main()


# #find setting in doc to fix port is in use > dynamically?
