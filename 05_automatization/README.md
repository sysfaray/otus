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
   log_format: Формат логов
httpserver:
    host: ip адрес сервера
    port: порт
    hostname: 
    root: Рутовая директория (default="/opt/httpd/web/")
    timeout: (default=5)
```
Запуск 

```python httpd.py```

Проверка тестов

```python httptest.py```

Тест нагрузки `ab -n 50000 -c 100 -r http://localhost/`

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