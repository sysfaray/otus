Требования

```Python3.6+```

Установка

```cd /opt/
   mkdir /httpd/
   git clone git@github.com:sysfaray/otus.git
   cp otus/05_automatization/homework/* /opt/httpd/
   cd httpd
   pip install -r req/install.txt
```

Конфигурация сервера лежит в etc/settings.yml, сама конфигурация находится в config.py
```
log:
   loglevel: Уровень логирования, по умолчанию (default="info")
   log_format: Формат логов (
            default="%(asctime)s [%(levelname)s] [%(name)s] [%(funcName)s] %(lineno)d: %(message)s")
httpserver:
    host: ip адрес сервера (default="127.0.0.1")
    port: порт (default=80)
    hostname: (default="localhost")
    root: Рутовая директория (default="/opt/httpd/web/")
    timeout: (default=5)
features:
    use_uvlib: Использование uvloop, вместо штатного loop (default=False)
    max_workers: Число потоков (default=1) 
```
Запуск 

```python httpd.py```

Проверка тестов

```python httptest.py```

Тест нагрузки без uvloop и с одним потоком `ab -n 50000 -c 100 -r http://localhost/`

```
This is ApacheBench, Version 2.3 <$Revision: 1430300 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        HTTPD
Server Hostname:        localhost
Server Port:            80

Document Path:          /
Document Length:        69 bytes

Concurrency Level:      100
Time taken for tests:   82.667 seconds
Complete requests:      50000
Failed requests:        0
Write errors:           0
Non-2xx responses:      50000
Total transferred:      10300000 bytes
HTML transferred:       3450000 bytes
Requests per second:    604.84 [#/sec] (mean)
Time per request:       165.333 [ms] (mean)
Time per request:       1.653 [ms] (mean, across all concurrent requests)
Transfer rate:          121.68 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2   1.5      2      30
Processing:     5  163  31.0    153     401
Waiting:        3  102  44.3    103     399
Total:          5  165  31.1    155     402

Percentage of the requests served within a certain time (ms)
  50%    155
  66%    164
  75%    171
  80%    176
  90%    204
  95%    234
  98%    270
  99%    277
 100%    402 (longest request)
```

Тест с uvloop и 10 потоками

```
Server Software:        HTTPD
Server Hostname:        localhost
Server Port:            80

Document Path:          /
Document Length:        9 bytes

Concurrency Level:      100
Time taken for tests:   47.946 seconds
Complete requests:      50000
Failed requests:        85
   (Connect: 0, Receive: 0, Length: 85, Exceptions: 0)
Write errors:           0
Non-2xx responses:      50000
Total transferred:      7300000 bytes
HTML transferred:       450000 bytes
Requests per second:    1042.84 [#/sec] (mean)
Time per request:       95.892 [ms] (mean)
Time per request:       0.959 [ms] (mean, across all concurrent requests)
Transfer rate:          148.69 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2   1.2      1      23
Processing:     4   94  37.3     83     478
Waiting:        1   58  30.7     54     409
Total:          4   96  37.5     84     478

Percentage of the requests served within a certain time (ms)
  50%     84
  66%     90
  75%     96
  80%    101
  90%    126
  95%    157
  98%    236
  99%    283
 100%    478 (longest request)
 ```