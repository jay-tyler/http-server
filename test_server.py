# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket
import pytest
import server
from multiprocessing import Process


ADDR = ('127.0.0.1', 8000)
CRLF = b'\r\n'
DUMMY_DATE = "Sun, 21 Jul 2001 23:32:15 GTM"

STATUS200 = b"".join([b"HTTP/1.1 200 OK\r\n",
                      b"DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n",
                      b"SERVER: Python/2.7.6\r\n",
                      b"\r\n"])

STATUS500 = b"".join([b"HTTP 500 Internal Server Error\r\n",
                      b"DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n",
                      b"SERVER: Python/2.7.6\r\n",
                      b"\r\n"])

Response_SKEL = CRLF.join(["{Response} {requri} {protocol}",
                          "Host: {host}", "Date: {date}", CRLF]).lstrip(CRLF)

REQ_GOOD = Response_SKEL.format(Response='get',
                                requri='http://www.host.com/images',
                                protocol="HTTP/1.1",
                                host="www.host.com",
                                date=DUMMY_DATE)


REQ_BAD_METHOD = Response_SKEL.format(Response='post',
                                      requri='http://www.host.com/images',
                                      protocol="HTTP/1.1",
                                      host="www.host.com",
                                      date=DUMMY_DATE)


REQ_BAD_PROTOCOL = Response_SKEL.format(Response='get',
                                        requri='http://www.host.com/images',
                                        protocol="HTTP/1.0",
                                        host="www.host.com",
                                        date=DUMMY_DATE)


REQ_BAD_HOST = CRLF.join(["{Response} {requri} {protocol}",
                          "Date: {date}"]).lstrip(CRLF).format(
                                  Response='Get',
                                  requri='http://www.host.com/images',
                                  protocol="HTTP/1.1", date=DUMMY_DATE)


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


def parse_response(response):
    """Take an HTTP response and determine whether it is valid; will raise
    an appropriate error if not

    will validate the following:
        * Response is HTTP/1.1
        * Response include valid date
        * Response includes valid status code

    if these validations are met, then return status code from response"""
    response = response.strip(CRLF).strip()
    lines = response.split(CRLF)
    initial_line = lines[0]
    protocol = initial_line.split()[0].strip().upper()
    response_code = initial_line.split()[1].strip()
    headers = [line for line in lines if b':' in line]
    headers = [line.split(':')[0].strip().upper() for line in lines]
    # headers = [header.rstrip(b':').upper() for header in headers]
    #  Converting headers to set for ease of membership testing
    headers = set(headers)

    try:
        int(response_code)
    except ValueError:
        to_return = False
    else:
        if b'DATE' not in headers:
            to_return = False
        elif b'HTTP/1.1' not in protocol:
            to_return = False
        else:
            #  HTTP response passes all prior checks, pass response code back
            to_return = response_code
    return to_return


def test_start_server(server_process):
    """Dummy function to start server"""
    pass


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
    assert parse_response(response) == b'200'


def test_response_error():
    response = server.response_error(500, b"Internal Server Error")
    assert parse_response(response) == b'500'


def test_functional_test_of_bad_request(client_socket):

    client_socket.connect(ADDR)
    client_socket.sendall(b"Hello there.")
    while True:
        response = client_socket.recv(1024)
        if len(response) < 1024:
            break
    # import pdb; pdb.set_trace()
    assert parse_response(response) == b"405"


def test_functional_test_of_good_request(client_socket):

    client_socket.connect(ADDR)
    client_socket.sendall(REQ_GOOD)
    while True:
        response = client_socket.recv(1024)
        if len(response) < 1024:
            break
    assert parse_response(response) == b"200"
