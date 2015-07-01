# -*- coding: utf-8 -*-
import socket
import sys
import pytest
import server
from multiprocessing import Process

ADDR = ('127.0.0.1', 8010)  # port 0 may force os to find an open port

STATUS200 = b"""HTTP/1.1 200 OK\r\n
    DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n
    SERVER: Python/2.7.6\r\n
    \r\n"""

STATUS500 = b"""HTTP 500 Internal Server Error \r\n
    DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n
    SERVER: Python/2.7.6\r\n
    \r\n"""


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
    client_socket.connect(ADDR)
    return client_socket


def start_server(server_process):
    """Dummy function to start server"""
    pass


def test_response_ok():
    assert server.response_ok() == STATUS200


def test_response_error():
    assert server.response_error() == STATUS500


def test_functional_test_of_response(client_socket):
    client_socket.sendall("Hello there.")
    while True:
        response_back = client_socket.recv(1024)
        if len(response_back) < 1024:
            break
    assert STATUS200.split("\r\n")[0] == response_back.split("\r\n")[0]
