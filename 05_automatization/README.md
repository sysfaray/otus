Требования

```Python3.6+```

Установка

```cd /opt/
   mkdir /httpd/
   git clone git@github.com:sysfaray/otus.git
   cp otus/05_automatization/homework/* /opt/httpd/
   cd httpd
```

Запуск 

```
--host - ip addres
--port - port 
-w - число воркеров
-t - timeout
-r - root directory
-l - loglevel
python httpd.py --host 127.0.0.1 --port 80 -w 10 -l debug```

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
Time taken for tests:   66.251 seconds
Complete requests:      50000
Failed requests:        0
Write errors:           0
Total transferred:      9950000 bytes
HTML transferred:       3450000 bytes
Requests per second:    754.70 [#/sec] (mean)
Time per request:       132.502 [ms] (mean)
Time per request:       1.325 [ms] (mean, across all concurrent requests)
Transfer rate:          146.67 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2   0.7      2       8
Processing:     4  131   7.5    130     219
Waiting:        2   72  31.4     72     216
Total:          5  132   7.5    132     220
```

Тест с 10 потоками

```
Server Software:        HTTPD
Server Hostname:        localhost
Server Port:            80

Document Path:          /
Document Length:        9 bytes

Concurrency Level:      100
Time taken for tests:   29.631 seconds
Complete requests:      50000
Failed requests:        1
   (Connect: 0, Receive: 1, Length: 0, Exceptions: 0)
Write errors:           0
Total transferred:      6949861 bytes
HTML transferred:       449991 bytes
Requests per second:    1687.42 [#/sec] (mean)
Time per request:       59.262 [ms] (mean)
Time per request:       0.593 [ms] (mean, across all concurrent requests)
Transfer rate:          229.05 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.2      0       5
Processing:     0   59  31.9     59     386
Waiting:        0   55  30.2     54     313
Total:          0   59  31.9     60     386

Percentage of the requests served within a certain time (ms)
  50%     60
  66%     77
  75%     86
  80%     90
  90%     99
  95%    105
  98%    111
  99%    118
 100%    386 (longest request)
 ```