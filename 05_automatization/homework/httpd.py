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
    log_format = (
        "%(asctime)s [%(levelname)s] [%(name)s] [%(funcName)s] %(lineno)d: %(message)s"
    )
    logging.basicConfig(format=log_format, level=loglevel)


HEAD_TERMINATOR = "\r\n\r\n"
RX_HEAD = re.compile(r"^(?P<method>\w*) (?P<address>.*) (?P<protocol>HTTP\/\d+\.\d+)$")
LOG_LEVEL = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


class HTTPD:
    def __init__(self, host, port, timeout, root, loop=None):
        self._root = root
        self._timeout = timeout
        self._loop = loop or asyncio.get_event_loop()
        self._server = asyncio.start_server(
            self.new_session,
            host,
            port,
            loop=self._loop,
            reuse_address=None,
            reuse_port=True,
            backlog=200,
        )
        self._pid = os.getpid()

    def start(self):
        self._server = self._loop.run_until_complete(self._server)
        logging.info(
            "Listener Server on {}, pid {}".format(
                self._server.sockets[0].getsockname(), self._pid
            )
        )
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            pass

        self._server.close()
        self._loop.run_until_complete(self._server.wait_closed())
        self._loop.close()

    @asyncio.coroutine
    async def new_session(self, reader, writer):
        logging.info("New session started")
        try:
            await asyncio.wait_for(
                self.handle_connection(reader, writer), timeout=self._timeout
            )
        except asyncio.TimeoutError as te:
            logging.info(f"Time is up!{te}")
        finally:
            writer.close()
            logging.info("Writer closed")

    @asyncio.coroutine
    async def handle_connection(self, reader, writer):
        addr = writer.get_extra_info("peername")
        logging.info("Connection established with %s", addr)
        try:
            logging.info("Awaiting data")
            line = await reader.readuntil(HEAD_TERMINATOR.encode())
            logging.info("Finished await got %s" % line)
            revert_message = self.parse_message(line)
            # logging.info("Revert message: %s" % revert_message)
            writer.write(revert_message)
            await writer.drain()
        except asyncio.IncompleteReadError:
            pass
        finally:
            writer.close()

    def get_data(self, path, method):
        """
        """
        content_type = "text/plain"
        data = b"Not Found"
        status = "200 OK"
        _path = os.path.abspath(path).strip("/")
        source = os.path.abspath(os.path.join(self._root, _path))
        if method == "GET":
            if os.path.isdir(source):
                source = os.path.join(source, "index.html")
            if os.path.exists(source):
                data = open(source, mode="rb").read()
                content_type = mimetypes.guess_type(source)[0]
            else:
                status = (
                    "404 Not Found" if not os.path.isfile(source) else "403 Forbidden"
                )
        else:
            data = os.path.getsize(source)
        return status, data, content_type

    def parse_header_response(self, method, status, data, type_data="text/plain"):
        """
        """
        status_line = "HTTP/1.1 {}\r\n".format(status)
        headers = OrderedDict()
        headers["Date"] = time.strftime("%H:%M:%S %d.%m.%Y")
        headers["Server"] = "HTTPD 1/.0"
        headers["Content-Length"] = data if isinstance(data, int) else len(data)
        headers["Content-Type"] = type_data
        headers["Connection"] = "close"
        headers_str = "\r\n".join(
            ["{}: {}".format(key, headers[key]) for key in headers.keys()]
        )
        headers_str = status_line + headers_str + "\r\n\r\n"
        return headers_str.encode("utf-8")

    def parse_response(self, method, status, data, type_data=b"text/plain"):
        """
        """
        response = self.parse_header_response(
            method=method, status=status, data=data, type_data=type_data
        )
        if method != "HEAD":
            response += data
        return response

    def parse_message(self, message):
        """
        """
        u_message = message.decode("utf-8")
        info = u_message.split("\r\n", 1)[0]
        logging.info(info)
        macth = RX_HEAD.match(info)
        if macth:
            method = macth.group("method")
            address = macth.group("address")
        else:
            return b"Requies is not valid"
        if method not in ["HEAD", "GET"]:
            return self.parse_response(
                method=method,
                status="405 Method Not Allowed",
                data=b"Method Not Allowed",
                type_data=b"text/plain",
            )
        else:
            path = address
            if "#" in path:
                path, fragment = path.split("#", 1)
            if "?" in path:
                path, param = path.split("?", 1)
            if "%" in path:
                fragments_of_path = path.split("%")
                normalize_fragments_of_path = [
                    fragments_of_path[0],
                ]
                for symbol in fragments_of_path[1:]:
                    normalize_fragments_of_path.append(
                        bytes.fromhex(symbol[:2]).decode("utf-8")
                    )
                    normalize_fragments_of_path.append(symbol[2:])
                path = "".join(normalize_fragments_of_path)
            logging.info("PATH: %s", path)
            status, data, type_data = self.get_data(path=path, method=method)
            if path is "/":
                return self.parse_response(
                    method=method, status="200 OK", data=data, type_data=type_data
                )
            return self.parse_response(
                method=method, status=status, data=data, type_data=type_data
            )


def run():
    server = HTTPD(host=args.host, port=args.port, timeout=args.timeout, root=args.root)
    server.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Host", default="127.0.0.1", type=str)
    parser.add_argument("--port", help="Port", default=80, type=int)
    parser.add_argument("-w", "--workers", help="Worker slots", default=2, type=int)
    parser.add_argument("-t", "--timeout", help="Timeout", default=0.1, type=float)
    parser.add_argument(
        "-r",
        "--root",
        help="Root dir",
        default=os.path.abspath(os.path.join(os.path.curdir, "web")),
    )
    parser.add_argument("-l", "--loglevel", help="Log level", default="info", type=str)

    args = parser.parse_args()
    setup_logging(loglevel=LOG_LEVEL[args.loglevel])
    for i in range(args.workers):
        p = multiprocessing.Process(target=run)
        p.start()
