# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket
import sys
import os

ADDR = ('127.0.0.1', 8001)
CRLF = ('\r\n')
PROTOCOL = b'HTTP/1.1'
# Using this as a dummy var
foo_date = "Sun, 21 Jul 2001 23:32:15 GTM"
reqtypes = set(["POST", "GET", "PUT", "HEAD", "DELETE", "OPTIONS", "TRACE"])

RESPONSE = CRLF.join([
    b'HTTP/1.1 {response_code} {response_reason}',
    b'Content-Type: text/html; charset=UTF-8',
    b'Date: {date}', CRLF])


def parse_request(request):
    """Take an HTTP request and determine whether it is valid; will raise
    an appropriate error if not

    will validate the following:
        * Request is GET method
        * Request is HTTP/1.1
        * Request include valid host header
    if these validations are met, then return URI from request"""
    request = request.strip(CRLF).strip()
    lines = request.split(CRLF)
    initial_line = lines[0]
    # Get method from initial line, and strip any leading white-space
    # or CRLF chars. Also format to uppercase for consistent handling.
    reqmethod = initial_line.split()[0].strip().upper()
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


def response_ok(uri):
    """Return a status 200 HTTP response_ok"""

    return RESPONSE.format(response_code=b'200',
                           response_reason=b'OK', date=foo_date)


def response_error(code, reason_phrase):
    """Return a status 500 Internal Server Error"""

    return RESPONSE.format(response_code=b'500',
                           response_reason=b'OK', date=foo_date)


def resolve_uri(uri):
    """Takes a uri and returns the contents a tuple of (body, content-type)

    body:
    if uri points to a file, returns the contents of that file,
    if uri points to a dir, returns an html file outlining contents

    content-type:
    when possible, will return a content type that is consistent with the
    content-type HTTP header.

    invalid requests will raise an appropriate Python exception

    """
    if len(uri.split('//', 1)) == 2:
        # Case of absolute uri
        pth_lst = uri.split('/')[3:]  # Throw out 'http://www.anyhost.com' bits
    else:
        # Case of relative uri
        pth_lst = uri.split('/')
        if pth_lst[0] in set(["", "."]):
            # Case of starting path with either "/" or "./"
            pth_lst = pth_lst[1:]
    pth = ("/").join(pth_lst)

    return pth


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
                    try:
                        resp_uri = parse_request(msg)
                    except ValueError:
                        response = response_error(400, b"Bad Request")
                    except NotImplementedError:
                        response = response_error(505, b"Version Not Supported")
                    except IndexError:
                        response = response_error(405, b"Method Not Allowed")
                    except Exception:
                        response = response_error(500, b"Internal Server Error")
                    else:
                        response = response_ok(resp_uri)

                    conn.sendall(response)
                    conn.close()
                    break
            sys.stdout.write(msg)

        except KeyboardInterrupt:
            conn.close()
            break

if __name__ == '__main__':
    main()
