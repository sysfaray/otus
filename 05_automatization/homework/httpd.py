# python
import sys
import logging
import asyncio
import mimetypes
import re
import os
import time
import argparse
from core.comp import smart_bytes, smart_text
from collections import OrderedDict
from concurrent.futures.thread import ThreadPoolExecutor

# HTTP Config
from config import config

def setup_logging(loglevel=None):
  """
  Create new or setup existing logger
  """
  if not loglevel:
    loglevel = config.log.loglevel
  logger = logging.getLogger()
  if len(logger.handlers):
    # Logger is already initialized
    fmt = logging.Formatter(config.log.log_format, None)
    for hd in logging.root.handlers:
      if isinstance(hd, logging.StreamHandler):
        hd.stream = sys.stdout
      hd.setFormatter(fmt)
    logging.root.setLevel(loglevel)
  else:
    # Initialize logger
    logging.basicConfig(stream=sys.stdout, format=config.log.log_format, level=loglevel)
  logging.captureWarnings(True)


RX_HEAD = re.compile(r'^(?P<method>\w*) (?P<address>.*) (?P<protocol>HTTP\/\d+\.\d+)$')

def setup_asyncio() -> None:
    """
    Initial setup of asynci
    :return:
    """
    logging.info("Setting up asyncio event loop policy")
    if config.features.use_uvlib:
        try:
            import uvloop
            logging.info("Setting up libuv event loop")
            uvloop.install()
        except ImportError:
            logging.info("libuv is not installed, using default event loop")
    asyncio.set_event_loop_policy(EventLoopPolicy())

class EventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        try:
            return super().get_event_loop()
        except RuntimeError:
            loop = self.new_event_loop()
            self.set_event_loop(loop)
            return loop

class HTTPD(object):
  def __init__(self, root, workers):
    self._root = root or config.httpserver.root
    self._loop = asyncio.get_event_loop()
    self._executor = ThreadPoolExecutor(max_workers=workers or config.features.max_workers)
    self._server = asyncio.start_server(self.new_session, host=config.httpserver.host, port=config.httpserver.port, loop=self._loop)

  def start(self, and_loop=True):
    self._server = self._loop.run_until_complete(self._server)
    logging.info('Listening established on {0}, whith session timeout: {1}s, hostname: {2} '.format(self._server.sockets[0].getsockname(), config.httpserver.timeout, config.httpserver.hostname))
    if and_loop:
      self._loop.run_forever()

  def stop(self, and_loop=True):
    self._server.close()
    if and_loop:
      self._loop.close()

  def get_data(self, path):
    """
    """
    _path = smart_text(os.path.abspath(path).strip('/'))
    source = os.path.abspath(os.path.join(self._root, _path))
    if os.path.isdir(source):
      source = os.path.join(source, 'index.html')
    if os.path.exists(source):
      data = open(source, mode='rb').read()
      content_type = mimetypes.guess_type(source)[0]
      status = '200 OK'
    else:
      source = os.path.abspath(os.path.join(self._root, _path))
      data = 'Not Found'
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
    return smart_bytes(headers_str)

  def parse_response(self, method, status, data, type_data='text/plain'):
    """
    """
    response1 = self.parse_header_response(method=method, status=status, data=data, type_data=type_data)
    if method != 'HEAD':
      response1 += smart_bytes(data)
    return response1

  def parse_message(self, message):
    """
    """
    info = smart_text(message).split("\r\n", 1)[0]
    logging.info(info)
    macth = RX_HEAD.match(info)
    if macth:
      method = macth.group('method')
      address = macth.group('address')
    else:
      return 'Requies is not valid'
    if method not in ['HEAD', 'GET']:
      message = self.parse_response(method=method,
                                    status='405 Method Not Allowed',
                                    data='Method Not Allowed',
                                    type_data='text/plain')
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
          normalize_fragments_of_path.append(smart_text(bytes.fromhex(symbol[:2])))
          normalize_fragments_of_path.append(symbol[2:])
        path = ''.join(normalize_fragments_of_path)
      logging.info('PATH: %s', path)
      status, data, type_data = self.get_data(path=path)
      message = self.parse_response(method=method,
                                    status=status,
                                    data=data,
                                    type_data=type_data)
    return message

  @asyncio.coroutine
  async def new_session(self, reader, writer):
    logging.info("New session started")
    try:
       self._loop.run_in_executor(self._executor, await asyncio.wait_for(self.handle_connection(reader, writer), timeout=config.httpserver.timeout))
    except asyncio.TimeoutError as te:
      logging.info(f'Time is up!{te}')
    finally:
      writer.close()
      logging.info("Writer closed")

  @asyncio.coroutine
  async def handle_connection(self, reader, writer):
    addr = writer.get_extra_info('peername')
    logging.info('Connection established with %s', addr)
    try:
      keep_alive = True
      while keep_alive:
        keep_alive = False
        while True:
          logging.info('Awaiting data')
          line = await reader.read(1024)
          logging.info('Finished await got %s' % smart_text(line))
          if not line:
            logging.info('Connection terminated with %s', addr)
            break
          if re.match(rb'connection:\s*keep-alive', line, re.I):
            keep_alive = True
          revert_message = self.parse_message(line)
          logging.info(revert_message)
          writer.write(smart_bytes(revert_message))
          await writer.drain()
    finally:
      writer.close()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-w', '--workers',
                      help='Workers count',
                      type=int)
  parser.add_argument('-r', '--root',
                      help='Root dir')

  args = parser.parse_args()
  if args:
    workers = args.workers
    root = args.root
  setup_logging()
  setup_asyncio()
  serv = HTTPD(root, workers)
  try:
    serv.start()
  except KeyboardInterrupt:
    pass  # Press Ctrl+C to stop
  finally:
    serv.stop()
