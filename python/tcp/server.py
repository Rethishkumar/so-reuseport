import time
import logging
import threading
import concurrent.futures
from argparse import ArgumentParser
from worker import Server


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
        '-n', '--num_servers', type=int, default=1,
        dest='num_servers', help='Number of servers')

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
    import logging.config
    logging.config.dictConfig(DEFAULT_LOGGING)
    global CMD_OPTIONS
    if CMD_OPTIONS.verbose:
        l = logging.getLogger('')
        l.setLevel(logging.DEBUG)


def start_multithreaded_servers(ip: str, port: int, num_servers: int):
    LOG.info('starting %d servers', num_servers)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_servers) as executor:
        futures = {executor.submit(
            Server(ip, port, idx).start): idx for idx in range(num_servers)}
        for future in concurrent.futures.as_completed(futures):
            idx = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                LOG.exception('server: %d generated an exception', idx)
            else:
                LOG.info('server: %d exited', idx)

    # servers = {idx: threading.Thread(target=Server(ip, port, index=idx).start)
    #            for idx in range(num_servers)}
    # for server_idx in servers:
    #     LOG.info('starting server: %d', server_idx)
    #     servers[server_idx].start()

    # for server_idx in servers:
    #     servers[server_idx].join()
    #     LOG.info('server: %d joined', server_idx)


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    opts = get_options()
    configure_logging()

    if opts.multi_thread:
        start_multithreaded_servers(opts.ip, opts.port, opts.num_servers)

    time.sleep(600)


if __name__ == '__main__':
    main()
