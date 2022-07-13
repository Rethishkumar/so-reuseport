
import socket
import threading
import logging

LOG = logging.getLogger(__name__)


class Server:
    def __init__(self, ip: str, port: int) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._socket.bind((ip, port))
        LOG.info('server bound to %s', ((ip, port)))
        self._socket.listen()
        self._thread: threading.Thread = None

        self._is_stopped = False

    def start(self) -> None:
        self._thread = threading.Thread(
            target=self.serve_clients, daemon=True)
        self._thread.start()
        LOG.info('serve clients thread started')

    def stop(self) -> None:
        self._is_stopped = True
        LOG.debug('stop flagged')
        self._thread.join()
        LOG.debug('thread joined')

    def serve_clients(self) -> None:

        LOG.info('waiting for client connections')
        while not self._is_stopped:
            conn, addr = self._socket.accept()
            with conn:
                LOG.info('received connection from %s', addr)
                data = bytes()
                while True:
                    d = conn.recv(1024)
                    if not d:
                        break
                    LOG.debug('received %d bytes', len(d))
                    data += d
                LOG.info('received total %d bytes', len(data))
                conn.sendall(bytes('hello from the other side'))

        LOG.info('exiting from serve_clients')
