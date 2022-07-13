import time
import logging.config
from argparse import ArgumentParser
from multithread.worker import Server as MultiThreadedTCPServer


import logging
LOG = logging.getLogger(__name__)

DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 8080

CMD_OPTIONS = None

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'server': {
            'format': '{asctime}.{msecs:03.0f} {levelname} {module}:{lineno:d} {process:d}-{thread:d} {message}',
            'style': '{',
            "datefmt": "%s"
        }
    },
    'handlers': {
        'server': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': 'server.log',
            'level': 'DEBUG',
            "formatter": "server"
        }
    },
    'loggers': {
        '': {
            'handlers': ['server'],
            'level': 'INFO',
            "propagate": True,
        }
    }
}


def get_options():

    parser = ArgumentParser(
        prog='server', description='server that illustrates the usage of SO_REUSEPORT')

    parser.add_argument(
        '--ip', type=str, default=DEFAULT_IP, dest='ip',
        help='listener ip')

    parser.add_argument(
        '--port', type=str, default=DEFAULT_PORT, dest='port',
        help='listener port')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--multi_process', action='store_true',
        dest='multi_process',
        help='multiprocess workers')

    group.add_argument(
        '--multi_thread', action='store_true',
        dest='multi_thread',
        help='multithread workers')

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


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    opts = get_options()
    configure_logging()

    server = None
    if opts.multi_thread:
        server = MultiThreadedTCPServer(opts.ip, opts.port)

    server.start()
    time.sleep(600)
    server.stop()


if __name__ == '__main__':
    main()
