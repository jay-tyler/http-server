# -*- coding: utf-8 -*-
import socket
import sys

ADDR = ('127.0.0.1', 8000)  # port 0 may force os to find an open port


def setup_server():
    server_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(ADDR)
    server_socket.listen(1)
    return server_socket


def response_ok():
    """Return a status 200 HTTP response_ok"""

    response_ok = b"""HTTP/1.1 200 OK\r\n
    DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n
    SERVER: Python/2.7.6\r\n
    \r\n"""

    return response_ok


def response_error():
    """Return a status 500 Internal Server Error"""

    response_error = b"""HTTP 500 Internal Server Error \r\n
    DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n
    SERVER: Python/2.7.6\r\n
    \r\n"""

    return response_error


def main():
    server_socket = setup_server()

    while True:
        try:
            conn, addr = server_socket.accept()
            msg = ""
            while True:
                msg_chunk = conn.recv(1024)
                msg += msg_chunk
                if len(msg_chunk) < 1024:
                    conn.sendall(response_ok())
                    conn.close()
                    break
            sys.stdout.write(msg)

        except KeyboardInterrupt:
            conn.close()
            break

if __name__ == '__main__':
    main()
