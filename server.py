# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
import socket
import sys
import os
import mimetypes

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webroot')
ROOT = ROOT.encode('utf-8')
ADDR = (b'127.0.0.1', 8000)
CRLF = (b'\r\n')
PROTOCOL = b'HTTP/1.1'
# Using this as a dummy var
foo_date = b"Sun, 21 Jul 2001 23:32:15 GTM"
reqtypes = set([b"POST", b"GET", b"PUT", b"HEAD", b"DELETE", b"OPTIONS",
    b"TRACE"])


RESPONSE = CRLF.join([
    b'HTTP/1.1 {response_code} {response_reason}',
    b'Content-Type: {ctype}; charset=UTF-8',
    b'Date: {date}', CRLF, b'{message}'])


def parse_request(request):
    """Take an HTTP request and determine whether it is valid; will raise
    an appropriate error if not

    will validate the following:
        * Request is GET method
        * Request is HTTP/1.1
        * Request include valid host header
    if these validations are met, then return URI from request"""
    request = request.encode('utf-8') # TODO: would want to query encoding
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
    #  Grabbing each header from above, removing trailing colon and converting
    #  to uppercase
    headers = [header.rstrip(b':').upper() for header in headers]
    #  Converting headers to set for ease of membership testing
    headers = set(headers)
    if reqmethod not in reqtypes:
        #  HTTP request is invalid; containing fct should return
        #  400 Bad Request
        raise ValueError
    elif b'HTTP/1.1' not in protocol:
        #  HTTP request is for a different protocol; containing fct should
        #  return 505 HTTP Version Not Supported
        raise NotImplementedError
    elif b'GET' not in reqmethod:
        #  HTTP request is for unsupported method; containing fct should
        #  return 405 Method Not Allowed
        raise IndexError
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
    message, ctype = resolve_uri(uri)
    return RESPONSE.format(response_code=b'200',
                           response_reason=b'OK', date=foo_date,
                           ctype=ctype, message=message)


def response_error(code, reason_phrase):
    """Return an error response"""

    return RESPONSE.format(response_code=code,
                           response_reason=reason_phrase,
                           date=foo_date, ctype=b'text/plain', message="")


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
    if len(uri.split(b'//', 1)) == 2:
        # Case of absolute uri
        pth_lst = uri.split(b'/')[3:]  # Throw out 'http://www.anyhost.com' bits
    else:
        # Case of relative uri
        pth_lst = uri.split(b'/')
        if pth_lst[0] in set([b"", b"."]):
            # Case of starting path with either "/" or "./"
            pth_lst = pth_lst[1:]
    pth = os.path.join(ROOT, *pth_lst)

    if os.path.isdir(pth):
        def pack_filenames():
            dirlist = os.walk(pth, topdown=True)
            _, _, filenames = next(dirlist)
            for filename in filenames:
                yield filename
        html_top = b'<html><head></head><body><ul>'
        body = CRLF.join([b"<li>{file}</li>".format(file=file)
                                    for file in pack_filenames()])
        html_end = b'</ul></body></html>'
        message = html_top + body + html_end
        ctype = b'text/html'

    elif os.path.exists(pth):
        with open(pth, 'r') as file:
            message = file.read()
        ctype = mimetypes.guess_type(pth)[0]

    else:
        raise LookupError  # For 404

    print pth, ROOT
    return message, ctype

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
                        response = response_ok(resp_uri)
                    except ValueError:
                        response = response_error(400, b"Bad Request")
                    except NotImplementedError:
                        response = response_error(505, b"Version Not Supported")
                    except IndexError:
                        response = response_error(405, b"Method Not Allowed")
                    except LookupError:
                        response = response_error(404, b"Not Found")
                    except Exception:
                        response = response_error(500, b"Internal Server Error")
                    conn.sendall(response)
                    conn.close()
                    break
            sys.stdout.write(msg)

        except KeyboardInterrupt:
            conn.close()
            break

if __name__ == '__main__':
    main()
