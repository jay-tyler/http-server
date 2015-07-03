# -*- coding: utf-8 -*-
import socket
import sys

ADDR = ('127.0.0.1', 8024)

CRLF = b'\r\n'
GET = b'GET'
PROTOCOL = b'HTTP/1.1'
HOST_PREFIX = b'Host:'


Response = CRLF.join([
    b'HTTP/1.1 {response_code} {response_reason}',
    b'Content-Type: text/html; charset=UTF-8',
    b''])

def parse_request(request):
    lines = request.split(CRLF)
    header = lines[0]
    header_pieces = header.split()
    if header_pieces[0] != GET:
        raise TypeError(b'Method Not Allowed')
    elif header_pieces[2] != PROTOCOL:
        raise ValueError(b'HTTP Version Not Supported')
    host_line = lines[1]
    host_line_pieces = host_line.split()
    if lines[2] != b'':
        raise SyntaxError(b'Bad Request')
    if host_line_pieces[0] != HOST_PREFIX:
        raise Exception(b'Bad Request')
    else:
        return header_pieces[1]

def setup_server():
    server_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(ADDR)
    server_socket.listen(1)
    return server_socket


def response_ok():
    return Response.format(response_code=b'200',
                           response_reason=b'OK')

def response_error():
    return Response.format(response_code=b'200',
                           response_reason=b'response_reason')

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
            try:
                parse_request(msg)
            except SyntaxError:
                response_error(400, "Invalid SyntaxError")
            except ValueError:
                response_error(400, "Value Error")
            sys.stdout.write(msg)
            conn.close()
            break
        except KeyboardInterrupt:
            conn.close()
            break

if __name__ == '__main__':
    main()