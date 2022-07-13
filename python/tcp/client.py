from asyncio.log import logger
import logging
import concurrent.futures
from typing import List
from argparse import ArgumentParser
import logging.config
import time
import socket

LOG = logging.getLogger(__name__)

DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 8080

CMD_OPTIONS = None

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'client': {
            'format': '{asctime}.{msecs:03.0f} {levelname} {module}:{lineno:d} {process:d}-{thread:d} {message}',
            'style': '{',
            "datefmt": "%s"
        }
    },
    'handlers': {
        'client': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': 'client.log',
            'level': 'DEBUG',
            "formatter": "client"
        }
    },
    'loggers': {
        '': {
            'handlers': ['client'],
            'level': 'INFO',
            "propagate": True,
        }
    }
}


def get_options():

    parser = ArgumentParser(
        prog='client', description='client that illustrates the usage of SO_REUSEPORT')

    parser.add_argument(
        '--ip', type=str, default=DEFAULT_IP, dest='ip',
        help='listener ip')

    parser.add_argument(
        '--port', type=str, default=DEFAULT_PORT, dest='port',
        help='listener port')

    parser.add_argument(
        '-n', '--num_clients', type=int, default=1,
        dest='num_clients', help='Number of clients')

    parser.add_argument(
        '-m', '--messages_per_second', type=int, default=2,
        dest='messages_per_second', help='Messages per second')

    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        dest='verbose',
        help='Verbose Logging')

    opts = parser.parse_args()

    global CMD_OPTIONS
    CMD_OPTIONS = opts
    LOG.debug('get_options %s', CMD_OPTIONS)

    return opts


def configure_logging() -> None:

    import logging
    logging.config.dictConfig(DEFAULT_LOGGING)
    global CMD_OPTIONS
    if CMD_OPTIONS.verbose:
        l = logging.getLogger('')
        l.setLevel(logging.DEBUG)


def start_client(client_index: int, messages_per_second: int) -> None:

    LOG.info('client: %d starting ', client_index)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((DEFAULT_IP, DEFAULT_PORT))
        while True:
            LOG.debug('client: %d sending data')
            s.sendall(b"Hello, world")
            LOG.debug('client: %d receiving data')
            data = s.recv(1024)
            LOG.debug('client: %d data %s', data)
            time.sleep(1/messages_per_second)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    opts = get_options()
    configure_logging()

    with concurrent.futures.ThreadPoolExecutor(max_workers=opts.num_clients) as executor:
        futures = {executor.submit(
            start_client, idx, opts.messages_per_second): idx for idx in range(opts.num_clients)}
        for future in concurrent.futures.as_completed(futures):
            idx = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                logger.exception('client: %d generated an exception', idx)
            else:
                logger.info('client: %d exited')


if __name__ == '__main__':
    main()
