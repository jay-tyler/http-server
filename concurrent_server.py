# -*- coding: utf-8 -*-
import server


def set_server(conn, adr):
    while True:
        try:
            msg = ""
            while True:
                msg_chunk = conn.recv(64)
                msg += msg_chunk
                if len(msg_chunk) < 64:
                    try:
                        resp_uri = server.parse_request(msg)
                    except ValueError:
                        response = server.response_error(400, b"Bad Request")
                    except NotImplementedError:
                        response = server.response_error(505, b"Version Not Supported")
                    except IndexError:
                        response = server.response_error(405, b"Method Not Allowed")
                    except LookupError:
                        response = server.response_error(404, b"Not Found")
                    except Exception:
                        response = server.response_error(500, b"Internal Server Error")
                    else:
                        response = server.response_ok(resp_uri)

                    conn.sendall(response)
                    conn.close()

        except KeyboardInterrupt:
            break


def start_server():
    from gevent.server import StreamServer
    from gevent.monkey import patch_all
    patch_all()
    gserver = StreamServer(server.ADDR, set_server)
    print('Starting gen server using {}'.format(server.ADDR))
    gserver.serve_forever()


if __name__ == '__main__':
    start_server()
