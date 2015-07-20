import pytest
from server import response_ok


@pytest.fixture(scope='function')
def test_response():
    assert response_ok(client) ==  """ returns a response containg an inital response line, header, body"""
    response_ok = """HTTP/1.1 200 OK\r\n\
    DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n\
    SERVER: Python/2.7.6\r\n\
    \r\n\
    """

def test_response():
    assert response_error(client) ==  response_error = """HTTP 500 Internal Server Error \r\n\
    DATE: Sun, 21 Jul 2001 23:32:15 GTM\r\n\
    SERVER: Python/2.7.6\r\n\
    \r\n\
    """
