import socket
import sys

ADDR = ('127.0.0.1', 8001) #port 0 may force os to find an open port

def setup_server():
    server_socket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(ADDR)
    server_socket.listen(1) #1 is backlog of connections it will hold onto
    return server_socket


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


def parse_request(header):
    "phrase header, check values against method and proto"
    header = header.split('\r\n')
    first_line = header[0].split()
    try:
        method = first_line[0]
        uri = first_line[1]
    if method != 'GET' or proto != 'HTTP/1.1':
        return response_error(<code>,<reason>)

    except IndexError:
        pass
    return uri

def main():
    server_socket = setup_server()

    while True:
        try:
            conn, addr = server_socket.accept()
            msg = ""
            while True:
                msg_chunk = conn.recv(1024)
                msg += msg_chunk
                # conn.sendall(msg)
                if len(msg_chunk) < 1024:
                    # response_ok()
                    conn.sendall(msg)
                    conn.close()
                    break
            sys.stdout.write(msg)

        except KeyboardInterrupt:
            client.close()
            break

if __name__ == '__main__':
    main()
