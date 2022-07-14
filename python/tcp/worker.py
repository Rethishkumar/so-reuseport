
import socket
import select
from typing import Dict
import logging

LOG = logging.getLogger(__name__)


class Server:
    def __init__(self, ip: str, port: int, index: int) -> None:
        self._index = index
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._server.setblocking(False)
        self._server.bind((ip, port))
        LOG.info('server: %d server bound to %s', index, ((ip, port)))
        self._server.listen()
        self._is_stopped = False

    def start(self) -> None:
        self.serve_clients()

    def stop(self) -> None:
        self._is_stopped = True
        LOG.debug('stop flagged')
        self._thread.join()
        LOG.debug('thread joined')

    def serve_clients(self) -> None:

        clients: Dict[socket.socket, str] = {}
        while True:
            inputs = [self._server]
            inputs.extend(clients.keys())
            outputs = list(clients.keys())
            LOG.info('server: %d num clients: %d', self._index, len(clients))
            readable, writeable, exceptional = select.select(
                inputs, [], inputs, 600)

            ## Process the readables
            for s in readable:
                # Accept a new connection
                if s is self._server:
                    conn, addr = self._server.accept()
                    conn.setblocking(False)
                    LOG.info(
                        'server: %d client: %s. received connection', self._index, addr)
                    clients[conn] = addr
                    continue
                addr = clients[s]
                LOG.debug('server: %d client: %s. reading data',
                          self._index, addr)
                data = s.recv(1024)
                if data:
                    # send a response
                    LOG.info('server: %d client: %s. received data: %s',
                             self._index, addr, data.decode(encoding='utf8'))
                    s.sendall(
                        bytes(f'server: {self._index} received', encoding='utf8'))
                    continue

                # No data means the connection is closed
                LOG.info('server: %d client: %s. closing connection',
                         self._index, addr)
                clients.pop(s)
                s.close()

            for s in exceptional:
                addr = clients[s]
                LOG.info('server: %d client: %s. received exception',
                         self._index, addr)
                clients.pop(s)
                s.close()

            if writeable:
                LOG.info('writeable: %s', writeable)
