# Point to line on github yaml

Have you ever tries to point someone to some line to yaml on github? here is solution: 

```
curl -v '127.0.0.1:8888/ln?src=https://github.com/zalando/nakadi/blob/master/api/nakadi-event-bus-api.yaml&t=problem&t=definitions'
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 8888 (#0)
> GET /ln?src=https://github.com/zalando/nakadi/blob/master/api/nakadi-event-bus-api.yaml&t=problem&t=definitions HTTP/1.1
> Host: 127.0.0.1:8888
> User-Agent: curl/7.51.0
> Accept: */*
> 
< HTTP/1.1 302 Found
< Date: Wed, 14 Jun 2017 13:14:18 GMT
< Content-Length: 0
< Content-Type: text/html; charset=UTF-8
< Location: https://github.com/zalando/nakadi/blob/master/api/nakadi-event-bus-api.yaml#L1800
< Server: TornadoServer/4.4.2
< 
* Curl_http_done: called premature == 0
* Connection #0 to host 127.0.0.1 left intact

```

