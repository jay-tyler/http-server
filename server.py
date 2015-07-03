# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket
import sys


ADDR = ('127.0.0.1', 8001)
CRLF = ('\r\n')
PROTOCOL = b'HTTP/1.1'
# Using this as a dummy var
formatted_date = "Sun, 21 Jul 2001 23:32:15 GTM"
reqtypes = set(["POST", "GET", "PUT", "HEAD", "DELETE", "OPTIONS", "TRACE"])

Response = CRLF.join([
    b'HTTP/1.1 {response_code} {response_reason}',
    b'Content-Type: text/html; charset=UTF-8',
    b'Date: {formatted_date}',
    b''])


def parse_request(request):
    """Take an HTTP request and determine whether it is valid; will raise
    an appropriate error if not

    will validate the following:
        * Request is GET method
        * Request is HTTP/1.1
        * Request include valid host header
    if these validations are met, then return URI from request"""

    lines = request.split(CRLF)
    initial_line = lines[0]
    # Get method from initial line, and strip any leading white-space
    # or CRLF chars. Also format to uppercase for consistent handling.
    reqmethod = initial_line.split()[0].strip().lstrip(CRLF).upper()
    uri = initial_line.split()[1].strip()
    protocol = initial_line.split()[2].strip()
    #  Get headers by splitting response by CRLF and dropping the first line.
    headers = [line.split()[0].strip() for line in lines][1:]
    #  Grabbing each header from above, removing trailing colon and converting to uppercase
    headers = [header.rstrip(':').upper() for header in headers]
    #  Converting headers to set for ease of membership testing
    headers = set(headers)
    if reqmethod not in reqtypes:
        #  HTTP request is invalid; containing fct should return
        #  400 Bad Request
        raise ValueError
    elif b'GET' not in reqmethod:
        #  HTTP request is for unsupported method; containing fct should
        #  return 405 Method Not Allowed
        raise IndexError
    elif b'HTTP/1.1' not in protocol:
        #  HTTP request is for a different protocol; containing fct should
        #  return 505 HTTP Version Not Supported
        raise NotImplementedError
    elif b'HOST' not in headers:
        #  HTTP request is not properly formed; containing fct should
        #  return 400 Bad Request
        raise ValueError
    else:
        #  HTTP request passes all prior checks, pass URI back
        return uri

def setup_server():
    server_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(ADDR)
    server_socket.listen(1)
    return server_socket


def response_ok():
    """Return a status 200 HTTP response_ok"""

    response_ok = b"".join(["HTTP/1.1 200 OK\r\n",
                            "DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n",
                            "SERVER: Python/2.7.6\r\n",
                            "\r\n"])
    nowthis = Response.format(response_code=b'200', #TODO
                           response_reason=b'response_reason')

    return response_ok


def response_error():
    """Return a status 500 Internal Server Error"""

    response_error = b"".join(["HTTP 500 Internal Server Error\r\n",
                               "DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n",
                               "SERVER: Python/2.7.6\r\n",
                               "\r\n"])
    nowthis = Response.format(response_code=b'500', #TODO
                           response_reason=b'OK')
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
                    parse_request(msg)
                    # conn.sendall(response_ok())
                    conn.close()
                    break
            sys.stdout.write(msg)

        except KeyboardInterrupt:
            conn.close()
            break

if __name__ == '__main__':
    main()
