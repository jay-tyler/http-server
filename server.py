import socket

ADDR = ('127.0.0.1', 8015)

socket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)

socket.bind(ADDR)
socket.listen(1) #1 is backlog of connections it will hold onto

def response_ok():
    """ returns a response containg an inital response line, header, body"""
    response_ok = """HTTP/1.1 200 OK\r\n\
    DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n\
    SERVER: Python/2.7.6\r\n\
    \r\n\
    """
    return response_ok.encode('utf-8')

def response_error():
    "returns an an HTTP 500 error"
    response_error = """HTTP 500 Internal Server Error \r\n\
    DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n\
    SERVER: Python/2.7.6\r\n\
    \r\n\
    """
    return response_error.encode('utf-8')


def main():
    msg = ""
    while True:
        try:
            conn, addr =  socket.accept()
            while True:
                msg += conn.recv(16)
                conn.sendall(msg)
                if len(msg) <  16:
                    # response_ok()
                    conn.close()
                    break
        except KeyboardInterrupt:
            client.close()
            break
    sys.stdout.write(msg)
    



if __name__ == '__main__':
    main()


#find setting in doc to fix port is in use > dynamically?
