# red2ws
<h2>Pure python 2.X, 3.X WebSocket interface for redis</h2>
<h3>Connect to redis server using WebSockets from javascript and another langs</h3>
<h4>Use</h4>
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
<h3>Features</h3>
<ul>
  <li>Apache 2.0 license</li>
  <li>Python 2 & 3 compatibility</li>
  <li>Subscribe and publish from websocket. Support for WebSocket onmessage callback and suport for a websocket send commmand</li>
  <li>Javascript sample implementation in a sample html page test_red2ws.html</li>
  <li>Multi channel subscriptions (view sample html page)</li>
  <li>Subscription patterns using * ([ws/wss]://[host]:[port]/[websockurl]/Test* subscribe to Test1, Test2, etc channels)</li>
  <li>ssl for a Websocket & redis (rediscacerts, websocksslcertfile, websocksslkeyfile) and suport for ws and wss protocols</li>
  <li>support for any redis db id (redisdb)</li>
  <li>redis password protected (redispassword) </li>
  <li>custom url for a websockets [ws/wss]://[host]:[port]/[websockurl]/[Channel]</li>
  <li>custom ports for a redis and websock (websockport, redisport)</li>
  <li>custom host for a redis (redishost)</li>
  <li>Reusable and embeddable code</li>
</ul>
<h3>Quick Start</h3>
<ol>
  <li>Run red2ws: ./red2ws.py --debug=1</li>
  <li>Run ./examples/test_red2ws.html in your browser</li>
  <li>In the browser, click Add Channel Button <img src="https://raw.githubusercontent.com/ricardmaso/red2ws/master/img/Selecci%C3%B3n_194.png"></li>
  <li>Put channel id in the input channel</li>
  <li>Click connect button <img src="https://raw.githubusercontent.com/ricardmaso/red2ws/master/img/Selecci%C3%B3n_195.png"></li>
  <li>Publish data in redis to channel from command line with redis-cli publish [Channel] [Msg]</li>
  <li>Or publish in redis from publish button in a browser <img src="https://raw.githubusercontent.com/ricardmaso/red2ws/master/img/Selecci%C3%B3n_196.png"></li>
</ol>
