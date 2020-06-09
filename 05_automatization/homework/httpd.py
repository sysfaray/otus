# python
import logging
import asyncio
import mimetypes
import re
import os
import time
import socket
import argparse
from collections import OrderedDict
import multiprocessing


def setup_logging(loglevel):
    """
  Create new or setup existing logger
  """
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] [%(funcName)s] %(lineno)d: %(message)s"
    logging.basicConfig(format=log_format, level=loglevel)


RX_HEAD = re.compile(r'^(?P<method>\w*) (?P<address>.*) (?P<protocol>HTTP\/\d+\.\d+)$')
LOG_LEVEL = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG
}


class HTTPD:
    def __init__(self, protocol, config, loop=None):
        self._root = config['root']
        self._timeout = config['timeout']
        self._workers = config['workers']
        self._protocol = protocol
        self._loop = None
        self._server = None
        self._pid = os.getpid()
        self._host = config['host']
        self._port = config['port']

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self._loop = asyncio.get_event_loop()

        coro = self._loop.create_server(
            lambda: self._protocol(self._root),
            host=self._host,
            port=self._port,
            family=socket.AF_INET,
            reuse_port=True,
        )
        self._server = self._loop.run_until_complete(coro)

        logging.info('Listener Server on {}, pid {}'.format(
            self._server.sockets[0].getsockname(),
            self._pid
        ))
        self._loop.run_forever()

    def close(self):
        self._server.close()
        self._loop.run_until_complete(self._server.wait_closed())
        self._loop.close()


class ProtocolEcho(asyncio.Protocol):
    def __init__(self, root):
        self._root = root

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        logging.info('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        logging.info('Data received: {!r}'.format(message))
        revert_message = self.parse_message(data)
        logging.info('Send: {!r}'.format(revert_message))
        self.transport.write(revert_message)
        logging.info('Close the client socket')
        self.transport.close()

    def get_data(self, path):
        """
    """
        _path = os.path.abspath(path).strip('/')
        source = os.path.abspath(os.path.join(self._root, _path))
        if os.path.isdir(source):
            source = os.path.join(source, 'index.html')
        if os.path.exists(source):
            data = open(source, mode='rb').read()
            content_type = mimetypes.guess_type(source)[0]
            status = '200 OK'
        else:
            source = os.path.abspath(os.path.join(self._root, _path))
            data = b'Not Found'
            content_type = 'text/plain'
            status = '404 Not Found' if os.path.basename(source) != 'index.html' else '403 Forbidden'
        return status, data, content_type

    def parse_header_response(self, method, status, data, type_data='text/plain'):
        """
    """
        status_line = 'HTTP/1.1 {}\r\n'.format(status)
        headers = OrderedDict()
        headers['Date'] = time.strftime('%H:%M:%S %d.%m.%Y')
        headers['Server'] = 'HTTPD 1/.0'
        headers['Content-Length'] = len(data)
        headers['Content-Type'] = type_data
        headers['Connection'] = 'close'
        headers_str = '\r\n'.join(['{}: {}'.format(key, headers[key]) for key in headers.keys()])
        headers_str = status_line + headers_str + '\r\n\r\n'
        return headers_str.encode('utf-8')

    def parse_response(self, method, status, data, type_data=b'text/plain'):
        """
    """
        response1 = self.parse_header_response(method=method, status=status, data=data, type_data=type_data)
        if method != 'HEAD':
            response1 += data
        return response1

    def parse_message(self, message):
        """
    """
        u_message = message.decode("utf-8")
        info = u_message.split("\r\n", 1)[0]
        logging.info(info)
        macth = RX_HEAD.match(info)
        if macth:
            method = macth.group('method')
            address = macth.group('address')
        else:
            return b'Requies is not valid'
        if method not in ['HEAD', 'GET']:
            return self.parse_response(method=method,
                                       status='405 Method Not Allowed',
                                       data=b'Method Not Allowed',
                                       type_data=b'text/plain')
        else:
            path = address
            if '#' in path:
                path, fragment = path.split('#', 1)
            if '?' in path:
                path, param = path.split('?', 1)
            if '%' in path:
                fragments_of_path = path.split('%')
                normalize_fragments_of_path = [fragments_of_path[0], ]
                for symbol in fragments_of_path[1:]:
                    normalize_fragments_of_path.append(bytes.fromhex(symbol[:2]).decode('utf-8'))
                    normalize_fragments_of_path.append(symbol[2:])
                path = ''.join(normalize_fragments_of_path)
            logging.info('PATH: %s', path)

            status, data, type_data = self.get_data(path=path)
            if path == "/":
                return self.parse_response(method=method,
                                           status="200 OK",
                                           data=data,
                                           type_data=type_data)
            return self.parse_response(method=method,
                                       status=status,
                                       data=data,
                                       type_data=type_data)


def create_tcp_srv(params):
    server = HTTPD(ProtocolEcho, params)
    try:
        server.run()
    except KeyboardInterrupt:
        server.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',
                        help='Host',
                        default='127.0.0.1',
                        type=str)
    parser.add_argument('--port',
                        help='Port',
                        default=80,
                        type=int)
    parser.add_argument('-w', '--workers',
                        help='Worker slots',
                        default=2,
                        type=int)
    parser.add_argument('-t', '--timeout',
                        help='Timeout',
                        default=0.1,
                        type=float)
    parser.add_argument('-r', '--root',
                        help='Root dir',
                        default=os.path.abspath(os.path.join(os.path.curdir, 'web')))
    parser.add_argument('-l', '--loglevel',
                        help='Log level',
                        default=LOG_LEVEL["info"],
                        type=str)

    args = parser.parse_args()
    params = dict(
        host=args.host,
        port=args.port,
        root=args.root,
        workers=args.workers,
        timeout=args.timeout,
    )
    setup_logging(loglevel=LOG_LEVEL[args.loglevel])

    srvproclist = list()
    for i in range(args.workers):
        p = multiprocessing.Process(
            target=create_tcp_srv,
            args=(params,)
        )
        srvproclist.append(p)

    for proc in srvproclist:
        proc.start()

    for proc in srvproclist:
        proc.join()


if __name__ == '__main__':
    main()
