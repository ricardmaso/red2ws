# red2ws
<h2>Pure python 2.X, 3.X WebSocket interface for redis</h2>
<h3>Use</h3>
run: ./red2ws.py
<br>
help: ./red2ws.py --help
<br>
run with debug active: ./red2ws.py --debug=1 
<br>
Connect from javascript to channel test websocket with a url http://[server]:[Websockport]/[Channel]  (http://localhost:8080/test)
other parameters
<ul>
  <li>./red2ws.py --websockport=8888 (specify websocket port. Default 8080)</li>
  <li>./red2ws.py --websockhost=127.0.0.1 (specify allowed source connection. Default 0.0.0.0 (all))</li>
  <li>./red2ws.py --websockurl=/subscribe/(.+) (specify url. Default /(.+) (.+) is a channel variable the default connect url is http://server:port/[Channel]</li>
  <li>./red2ws.py --redishost=127.0.0.1 (specify redis host. Default 127.0.0.1)</li>
  <li>./red2ws.py --redisport=8080 (specify redis port. Default 8080)</li>
  <li>./red2ws.py --redispassword=password (specify redis password. Default "")</li>
  <li>./red2ws.py --rediscacerts=PATH_TO_CA (specify redis ca certs for a ssl connections. Default "")</li>
  <li>./red2ws.py --redisdb=0 (specify redis db. Default 0)</li>
  <li>./red2ws.py --debug=1 (activate log debug. Logger to terminal and file red2ws.log Default 0)</li>
  <li>./red2ws.py -websocksslcertfile=[PATH_TO_CERT_FILE] (if websocket connection over ssl, cert file. The protocol for url connection is wss:// if ssl or ws:// for not secure connection. Default "")</li>
<li>./red2ws.py -websocksslkeyfile=[PATH_TO_CERT_FILE] (if websocket connection over ssl, key file. The protocol for url connection is wss:// if ssl or ws:// for not secure connection. Default "")</li>
</ul>

<h3>Quick Start</h3>
<ol>
  <li>Run red2ws: ./red2ws.py --debug=1</li>
  <li>Run ./examples/test_red2ws.html in your browser</li>
  <li>In the browser, click Add Channel Button <img src="https://raw.githubusercontent.com/ricardmaso/red2ws/master/img/Selecci%C3%B3n_196.png"></li>
  <li>Put channel id in the input channel</li>
  <li>Click connect button</li>
  <li>Publish data in redis to channel from command line with redis-cli publish [Channel] [Msg]</li>
  <li>Or publish in redis from publish button in a browser</li>
</ol>
