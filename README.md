# red2ws
<h2>Pure python WebSocket interface for redis</h2>
run ./red2ws.py
help ./red2ws.py --help
run with debug active ./red2ws.py --debug=1 

Connect from javascript to channel test websocket with a url http://[server]:[Websockport]/[Channel]  (http://localhost:8080/test)
other parameters
<ul>
  <li>./red2ws.py --websockport=8888 (specify websocket port. Default 8080)</li>
  <li>./red2ws.py --websockhost=127.0.0.1 (specify allowed source connection. Default 0.0.0.0 (all))</li>
  <li>./red2ws.py --websockurl=/subscribe/(.+) (specify url. Default /(.+) (.+) is a channel variable the default connect url is http://server:port/[Channel]</li>
  <li>./red2ws.py --redishost=127.0.0.1 (specify redis host. Default 127.0.0.1)</li>
  <li>./red2ws.py --redisport=8080 (specify redis port. Default 8080)</li>
  <li>./red2ws.py --debug=1 (activate log debug. Logger to terminal and file red2ws.log Default 0)</li>
</ul>
