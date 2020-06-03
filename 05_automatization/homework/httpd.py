# python
import socket
import sys
import logging
import asyncio
import mimetypes
import re
import os
import time
from core.comp import smart_bytes, smart_text
from collections import OrderedDict
# WEB
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
    for h in logging.root.handlers:
      if isinstance(h, logging.StreamHandler):
        h.stream = sys.stdout
      h.setFormatter(fmt)
    logging.root.setLevel(loglevel)
  else:
    # Initialize logger
    logging.basicConfig(stream=sys.stdout, format=config.log.log_format, level=loglevel)
  logging.captureWarnings(True)


RE_HEAD = re.compile(r'^(?P<method>\w*) (?P<address>.*) (?P<protocol>HTTP\/\d+\.\d+)$')

class HTTPD(object):
  def __init__(self, host, port, loop=None):
    self._root = config.httpserver.root
    self._loop = loop or asyncio.get_event_loop()
    self._server = asyncio.start_server(self.handle_connection, host=host, port=port)
    self.executor = 3

  def start(self, and_loop=True):
    self._server = self._loop.run_until_complete(self._server)
    logging.info('Listening established on {0}'.format(self._server.sockets[0].getsockname()))
    if and_loop:
      self._loop.run_forever()

  def stop(self, and_loop=True):
    self._server.close()
    if and_loop:
      self._loop.close()

  def get_data(self, path):
    """
    Получение запрашиваемых данных
    :param str|unicode method: метод запроса сообщения
    :param str|unicode path: путь к запрашиваемому файлу или директории
    :return: статус, данные, тип передаваемых данных
    :rtype: tuple([str], [str], [bytes])
    """
    _path = smart_text(os.path.abspath(path).strip('/'))
    source = os.path.abspath(os.path.join(self._root, _path))
    print("@@@@")
    print(source)

    if os.path.isdir(source):
      source = os.path.join(source, 'index.html')
    if os.path.exists(source):
      data = open(source, mode='rb').read()
      content_type = mimetypes.guess_type(source)[0]
      status = '200 OK'
    else:
      data = 'Not Found'
      content_type = 'text/plain'
      status = '404 Not Found' if os.path.basename(source) != 'index.html' else '403 Forbidden'
    return status, data, content_type



  def parse_header_response(self, method, status, data, type_data='text/plain'):
    """
    Формирование заголовков ответного сообщения
    :param str|unicode method: тип HTTP-запроса
    :param str|unicode status: статус ответа
    :param str|unicode data: передаваемые данные
    :param str|unicode type_data: тип передаваемых данных
    :return: ответное сообщение
    :rtype: bytes
    """
    status_line = 'HTTP/1.1 {}\r\n'.format(status)
    headers = OrderedDict()
    headers['Accept'] = '*/*'
    headers['Accept-Encoding'] = '*'
    headers['Connection'] = 'close'
    headers['Server'] = 'HTTPD 1/.0'
    headers['Allow'] = 'GET, HEAD'
    headers['Content-Length'] = len(data)
    headers['Content-Type'] = type_data
    headers['Date'] = time.strftime('%H:%M:%S %d.%m.%Y')

    headers_str = '\r\n'.join(['{}: {}'.format(key, headers[key]) for key in headers.keys()])
    headers_str = status_line + headers_str + '\r\n\r\n'
    return smart_bytes(headers_str)


  def parse_response(self, method, status, data, type_data='text/plain'):
    """
    Формирование ответного сообщения
    :param str|unicode method: тип HTTP-запроса
    :param str|unicode status: статус ответа
    :param bytes data: передаваемые данные
    :param str|unicode type_data: тип передаваемых данных
    :return: ответное сообщение
    :rtype: bytes
    """
    response1 = self.parse_header_response(method=method, status=status, data=data, type_data=type_data)
    if method != 'HEAD':
      response1 += smart_bytes(data)
    return response1



  def parse_message(self, message):
    """
    Парсинг очередного сообщения
    :param bytes message: полученное сообщение
    :return: обратное сообщения для клиента
    :rtype: bytes
    """
    info = smart_text(message).split("\r\n", 1)[0]
    logging.info(info)
    macth = RE_HEAD.match(info)
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
      #  Удаление якоря
      if '#' in path:
        path, fragment = path.split('#', 1)
      #  Удаление параметров
      if '?' in path:
        path, param = path.split('?', 1)
      #  Нормализация адреса
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
  async def handle_connection(self, reader, writer):
    addr = writer.get_extra_info('peername')
    logging.info('Connection established with {}'.format(addr))
    try:
      keep_alive = True
      while keep_alive:
        keep_alive = False
        while True:
          logging.info('Awaiting data')
          # Read the marker
          line = await reader.readline()
          logging.info('Finished await got %s' % smart_text(line))
          if line.rstrip(b'\r\n'):
            if re.match(rb'connection:\s*keep-alive', line, re.I):
              keep_alive = True
            revert_message = self.parse_message(line)
            logging.info(revert_message)
            writer.write(smart_bytes(revert_message))
            await writer.drain()
          else:
            logging.info('Connection terminated with {}'.format(addr))
            break
    finally:
      writer.close()


if __name__ == '__main__':
  setup_logging()
  serv = HTTPD(config.httpserver.host, config.httpserver.port)
  try:
    serv.start()
  except KeyboardInterrupt:
    pass  # Press Ctrl+C to stop
  finally:
    serv.stop()
