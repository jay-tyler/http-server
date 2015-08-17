# -*- coding: utf-8 -*-
import socket
import pytest
import server
from multiprocessing import Process


###################################################
# Constants
###################################################
ADDR = (b'127.0.0.1', 8004)
CRLF = b'\r\n'
DUMMY_DATE = b"Sun, 21 Jul 2001 23:32:15 GTM"

STATUS200 = b"".join([b"HTTP/1.1 200 OK\r\n",
                      b"DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n",
                      b"SERVER: Python/2.7.6\r\n",
                      b"\r\n"])

STATUS500 = b"".join([b"HTTP 500 Internal Server Error\r\n",
                      b"DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n",
                      b"SERVER: Python/2.7.6\r\n",
                      b"\r\n"])

Response_SKEL = CRLF.join([b"{Response} {requri} {protocol}",
                          b"Host: {host}", "Date: {date}", CRLF]).lstrip(CRLF)

REQ_GOOD = Response_SKEL.format(Response=b'get',
                                requri=b'http://www.host.com/images',
                                protocol=b"HTTP/1.1",
                                host=b"www.host.com",
                                date=DUMMY_DATE)


REQ_BAD_METHOD = Response_SKEL.format(Response=b'post',
                                      requri=b'http://www.host.com/images',
                                      protocol=b"HTTP/1.1",
                                      host=b"www.host.com",
                                      date=DUMMY_DATE)


REQ_BAD_PROTOCOL = Response_SKEL.format(Response=b'get',
                                        requri=b'http://www.host.com/images',
                                        protocol=b"HTTP/1.0",
                                        host=b"www.host.com",
                                        date=DUMMY_DATE)


REQ_BAD_HOST = CRLF.join([b"{Response} {requri} {protocol}",
                          b"Date: {date}"]).lstrip(CRLF).format(
                                  Response=b'Get',
                                  requri=b'http://www.host.com/images',
                                  protocol=b"HTTP/1.1", date=DUMMY_DATE)


###################################################
# Fixtures
###################################################
@pytest.yield_fixture()
def server_process():
    process = Process(target=server.main)
    process.daemon = True
    process.start()
    yield process


@pytest.fixture()
def client_socket():
    client_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
        )
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return client_socket


###################################################
# Helper Functions
###################################################
def parse_response(response):
    """Take an HTTP response and determine whether it is valid; will raise
    an appropriate error if not

    will validate the following:
        * Response is HTTP/1.1
        * Response include valid date
        * Response includes valid status code

    if these validations are met, then return status code from response
    as well as the body as (status_code, body)"""
    response = response.strip(CRLF).strip()
    lines = response.split(CRLF)
    initial_line = lines[0]
    protocol = initial_line.split()[0].strip().upper()
    response_code = initial_line.split()[1].strip()
    headers = [line for line in lines if b':' in line]
    headers = [line.split(b':')[0].strip().upper() for line in lines]
    headers = set(headers)

    try:
        int(response_code)
    except ValueError:
        to_return = False, None
    else:
        if b'DATE' not in headers:
            to_return = False, None
        elif b'HTTP/1.1' not in protocol:
            to_return = False, None
        else:
            #  HTTP response passes all prior checks, pass response code back
            to_return = response_code, lines[-1]
    return to_return


###################################################
# Tests of Functions
###################################################
def test_parse_good_request():
    assert server.parse_request(REQ_GOOD) == b"http://www.host.com/images"


def test_parse_bad_method_request():
    with pytest.raises(IndexError):
        server.parse_request(REQ_BAD_METHOD)


def test_parse_bad_protocol_request():
    with pytest.raises(NotImplementedError):
        server.parse_request(REQ_BAD_PROTOCOL)


def test_parse_bad_host_request():
    with pytest.raises(ValueError):
        server.parse_request(REQ_BAD_HOST)


def test_response_ok():
    foo_uri = b'http://www.host.com'
    response = server.response_ok(foo_uri)
    assert parse_response(response)[0] == '200'


def test_response_error():
    response = server.response_error(500, b"Internal Server Error")
    assert parse_response(response)[0] == '500'


def test_resolve_uri_file():
    body, ctype = server.resolve_uri("http://www.host.com/sample.txt")
    assert ctype == b'text/plain'
    assert body is not None


def test_resolve_uri_file():
    body, ctype = server.resolve_uri("http://www.host.com/sample.txt")
    assert ctype == b'text/plain'
    assert b'This is a very simple text file.' in body


def test_resolve_uri_dir():
    body, ctype = server.resolve_uri("http://www.host.com/")
    assert ctype == b'text/html'
    assert b'a_web_page.html' in body
    assert b'JPEG_example.jpg' not in body


def test_resolve_uri_invalid():
    with pytest.raises(LookupError):
        server.resolve_uri("http://www.host.com/blah")


###################################################
# Functional Tests
###################################################
def test_functional_test_of_bad_request(server_process, client_socket):
    client_socket.connect(ADDR)
    client_socket.sendall(b"Hello there.")
    while True:
        response = client_socket.recv(1024)
        if len(response) < 1024:
            break
    # import pdb; pdb.set_trace()
    assert parse_response(response)[0] == "405"


def test_functional_test_of_good_request(server_process, client_socket):
    client_socket.connect(ADDR)
    client_socket.sendall(REQ_GOOD)
    while True:
        response = client_socket.recv(1024)
        if len(response) < 1024:
            break
    assert parse_response(response)[0] == "200"


def test_functional_request_of_dir(server_process, client_socket):
    request = Response_SKEL.format(Response=b'get',
        requri=b'http://www.host.com/',
        protocol=b"HTTP/1.1", host=b"www.host.com",
        date=DUMMY_DATE)   

    client_socket.connect(ADDR)
    client_socket.sendall(request)
    while True:
        response = client_socket.recv(1024)
        if len(response) < 1024:
            break
    assert b'text/html' in response
    assert parse_response(response)[0] == b'200'
    assert b'a_web_page.html' in response
    assert b'JPEG_example.jpg' not in response


def test_functional_request_of_dir(server_process, client_socket):
    request = Response_SKEL.format(Response=b'get',
        requri=b'http://www.host.com/',
        protocol=b"HTTP/1.1", host=b"www.host.com",
        date=DUMMY_DATE)   

    client_socket.connect(ADDR)
    client_socket.sendall(request)
    while True:
        response = client_socket.recv(1024)
        if len(response) < 1024:
            break
    assert b'text/html' in response
    assert parse_response(response)[0] == b'200'
    assert b'a_web_page.html' in response
    assert b'JPEG_example.jpg' not in response


def test_functional_request_of_text_file(server_process, client_socket):
    request = Response_SKEL.format(Response=b'get',
        requri=b'http://www.host.com/sample.txt',
        protocol=b"HTTP/1.1", host=b"www.host.com",
        date=DUMMY_DATE)   

    client_socket.connect(ADDR)
    client_socket.sendall(request)
    while True:
        response = client_socket.recv(1024)
        if len(response) < 1024:
            break
    assert b'text/plain' in response
    assert parse_response(response)[0] == b'200'
    assert b'This is a very simple text file.' in response


def test_functional_request_of_image_file(server_process, client_socket):
    request = Response_SKEL.format(Response=b'get',
        requri=b'http://www.host.com/images/JPEG_example.jpg',
        protocol=b"HTTP/1.1", host=b"www.host.com",
        date=DUMMY_DATE)

    client_socket.connect(ADDR)
    client_socket.sendall(request)
    response = ""
    while True:
        acc = client_socket.recv(1024)
        response += acc
        if len(acc) < 1024:
            break
    code, body = parse_response(response)
    assert code == b'200'
    assert b'image/jpeg' in response[:-2]
