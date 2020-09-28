#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#


import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import redis
import threading
import time
import logging
import argparse
import traceback
import sys
import os
import warnings
warnings.filterwarnings('ignore')
try:
    import simplejson as json
except ImportError:
    import json
try:
    import asyncio
except ImportError:
    pass
class nsCaptureException(object):    
    iType=""
    @property
    def Type(self):return str(self.iType)
    @Type.setter
    def Type(self,aValue):self.iType=aValue
    iValue=""
    @property
    def Value(self):return str(self.iValue)
    @Value.setter
    def Value(self,aValue):self.iValue=aValue
    iTrace=""
    @property 
    def Trace(self):return self.iTrace
    @property
    def TraceStr(self):return "".join(traceback.format_tb(self.iTrace)).replace("\n","").replace("  "," ")
    @Trace.setter
    def Trace(self,aValue):self.iTrace=aValue
    def __init__(self,aInfo):self.Type, self.Value, self.Trace = aInfo
    def __str__(self):return "Error:"+self.Value + " Type:" + self.Type + "TraceBack:" + self.TraceStr
    
def Bytes2Str(aValue):
    iRet=aValue
    try:
        if isinstance(aValue,bytes):
            iRet=aValue.decode('utf-8')
        else:
            iRet=str(aValue)
    except:
        pass
    return iRet
def IsPython3():return sys.version_info[0]>2
PYTHON3=IsPython3()
if PYTHON3:
    #Manage error when in tornado call write_message from another thread
    import tornado.platform.asyncio
    import asyncio
    asyncio.set_event_loop_policy(tornado.platform.asyncio.AnyThreadEventLoopPolicy())
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)
    
class WSHandler(tornado.websocket.WebSocketHandler):
    @property
    def Th(self):return self._Th
    @Th.setter
    def Th(self,aValue):self._Th=aValue
    @property
    def Parent(self):return self.application.Server
    @property
    def RemoteIp(self):return self.request.remote_ip
    @property
    def Key(self):return self._Key
    @Key.setter
    def Key(self,aValue):
        self._Key=aValue
    @property
    def Logger(self):
        if self._Logger==None:self._Logger=self.Parent.Logger
        return self._Logger
    @Logger.setter
    def Logger(self,aValue):self._Logger=aValue
    @property
    def Debug(self):
        if self._Debug==None:self._Debug=self.Parent.Debug
        return self._Debug
    @Debug.setter
    def Debug(self,aValue):self._Debug=aValue
    @property
    def Running(self):return self._Running
    @Running.setter
    def Running(self,aValue):self._Running=aValue
    @property
    def WebSockets(self):
        if self._WebSockets==None:self._WebSockets=self.Parent.WebSockets
        return self._WebSockets
    @WebSockets.setter
    def WebSockets(self,aValue):self._WebSockets=aValue
    @property
    def Redis(self):
        if self._Redis==None:self._Redis=self.Parent.Redis
        return self._Redis
    @Redis.setter
    def Redis(self,aValue):self._Redis=aValue

    @property
    def RedisWriter(self):
        if self._RedisWriter==None:self._RedisWriter=self.Parent.RedisWriter
        return self._RedisWriter
    @RedisWriter.setter
    def RedisWriter(self,aValue):self._RedisWriter=aValue

    @property
    def RedisSubscription(self):
        if self._RedisSubscription==None:
            self._RedisSubscription=self.Redis.pubsub()
            if self.Key[-1]!="*":
                self._RedisSubscription.subscribe(self.Key)
            else:
                self._RedisSubscription.psubscribe(self.Key)
        return self._RedisSubscription

    @RedisSubscription.setter
    def RedisSubscription(self,aValue):
        if self._RedisSubscription!=None:
            self._RedisSubscription.unsubscribe(self.Key)
        self._RedisSubscription=aValue

    def DebugMsg(self,aMsg):
        if self.Debug:self.Logger.debug(aMsg)


    def StartListener(self):
        if self.Running==False:
            if self not in self.WebSockets:
                self.WebSockets.append(self)
                self.Running=True
                self.Th=threading.Thread(target = self.Loop)
                self.Th.daemon=True
                self.Th.start()
        
    def StopListener(self):
        if self.Running:
            
            if self in self.WebSockets:
                self.RedisSubscription=None
                self.close()
                self.WebSockets.remove(self)
                self.Running=False
                
                self.Th=None
    def Loop(self):
        iMsg=None
        self.DebugMsg("Start Loop")
        while self.Running:
            time.sleep(0.001)
            try:
                iMsg=self.RedisSubscription.get_message(timeout=1)
                if iMsg:            
                    iChannel=Bytes2Str(iMsg['channel'])
                    iType=Bytes2Str(iMsg['type'])
                    iMatch=False
                    if self.Key[-1]=="*":
                        iMatch =self.Key[:-1] in iChannel
                    else:
                        iMatch=iChannel==self.Key
                    if iMatch:self.Write(json.dumps(iMsg))
                if self.Running==False:break
            except redis.ConnectionError as E:
                iError=str(E) + ":" + " Listener " + str(nsCaptureException(sys.exc_info())) + " (" + str(self.Key) + ":" + str(iMsg)  + ")"
                self.Logger.error(iError)  
            except Exception as E:
                iError = "red2ws.Loop(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info())) + " (" + str(iMsg) + ")"
                self.Logger.error(iError )    
        self.DebugMsg("Stop Loop")
                
    def open(self,aUrl):
        self._Contador=0
        self.Key=aUrl
        self.StartListener()
        self.DebugMsg("OPEN: " + aUrl +" channel " + str(self.Key) + " from " + self.RemoteIp)  
        time.sleep(.5)

    def on_message(self, message):
        self.RedisWriter.publish(self.Key,message)
    def check_origin(self, origin):return True

    def on_close(self,aCode = None, aReason = None):
        self.DebugMsg("DEBUG: CLOSE WS (" + str(self.Key) + ") from " + self.RemoteIp + " " + str(aCode) + ":" + str(aReason))
        self.StopListener()
    def Write(self,aMsg):
        try:
            iObj=aMsg
            self._Contador=self._Contador+1
            try:
                iData=iObj
                if PYTHON3:iData=iData.encode('utf-8')   
                self.write_message(iData)
            except tornado.websocket.WebSocketClosedError as E:
                pass
            except Exception as e:
                pass
            if self.Debug and self._Contador % 100 ==0:self.DebugMsg("DEBUG: PUBLISH WS (" + str(self.Id) + ") to " + self.RemoteIp + ": " + str(self._Contador))
        except Exception as E:
            iError = "WSHandler.Write(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info())) + " (" + self.Key + ":" + str(aMsg) +  ")"
            self.Parent.Logger.error(iError ) 
    def __init__(self, *args, **kwargs):        
        self._RedisSubscription=None
        self._Redis=None
        self._RedisWriter=None
        self._Th=None
        self._WebSockets=None
        self._Debug=None
        self._Contador=0
        self._Running=False
        self._Logger=None
        self._Parent=None
        self._Key=None
        self._Parent = kwargs.pop('aParent')
        super(WSHandler, self).__init__(*args, **kwargs)

class red2ws(object):
    @property
    def SslCertFile(self):return self._SslCertFile
    @SslCertFile.setter
    def SslCertFile(self,aValue):self._SslCertFile=aValue
    @property
    def SslKeyFile(self):return self._SslKeyFile
    @SslKeyFile.setter
    def SslKeyFile(self,aValue):self._SslKeyFile=aValue
    @property
    def Debug(self):return self._Debug
    @Debug.setter
    def Debug(self,aValue):self._Debug=aValue
    @property
    def LogFileName(self):
        if self._LogFileName==None:self._LogFileName=__file__+ ".log"
        return self._LogFileName
    @property
    def Logger(self):
        if self._Logger==None:
            self._Logger=logging.getLogger(os.path.basename(self.LogFileName).split(".")[0])
            self._Logger.setLevel(logging.DEBUG)
            iHandler=logging.handlers.RotatingFileHandler(self.LogFileName, maxBytes=10*1024*1024, backupCount=5)
            iFormater=logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            
            iHandler.setFormatter(iFormater)
            self._Logger.addHandler(iHandler)
            iHandler = logging.StreamHandler()
            iHandler.setFormatter(iFormater)
            self._Logger.addHandler(iHandler)
        return self._Logger
    @property
    def WebSockets(self):
        if self._WebSockets==None:self._WebSockets=self.Parent.WebSockets
        return self._WebSockets
    @WebSockets.setter
    def WebSockets(self,aValue):self._WebSockets=aValue
    @property
    def LocalIp(self):
        if self._LocalIp==None:self._LocalIp=socket.gethostbyname(socket.gethostname())
        return self._LocalIp
    @property
    def Url(self):
        if self._Url==None:self._Url=r'/(.+))'
        return self._Url
    @Url.setter
    def Url(self,aValue):self._Url=aValue
    @property
    def App(self):
        if self._App==None:
            self._App=tornado.web.Application([(self.Url, WSHandler,{'aParent':self})])
            self._App.Server=self
        return self._App
    @App.setter
    def App(self,aValue):self._App=aValue
    @property
    def Client(self):
        if self._Client==None:
            iSsl=None
            if os.path.exists(self.SslCertFile) and os.path.exists(self.SslKeyFile):iSsl={"certfile": self.SslCertFile,"keyfile": self.SslKeyFile}
            self._Client=tornado.httpserver.HTTPServer(self.App,ssl_options=iSsl)
            self._Client.listen(self.Port,address=self.Host)
        return self._Client
    @Client.setter
    def Client(self,aValue):
        self._Client=aValue

    @property
    def Port(self):return self._Port
    @Port.setter
    def Port(self,aValue):self._Port=aValue
        
    @property
    def Host(self):return self._Host
    @Host.setter
    def Host(self,aValue):self._Host=aValue
    def StartWs(self):
        iClient=self.Client
        tornado.ioloop.IOLoop.instance().start()
    def StopWs(self):
        tornado.ioloop.IOLoop.instance().stop()
        self.Client=None
    def Start(self):
        self.StartWs()
    def Stop(self):
        self.StopWs()
    def Reconnect(self,aMax=10):
        iRet=False
        iCont=1
        while 1:
            try:
                iCont=iCont+1
                self.Redis.ping()                
            except redis.ConnectionError as E:
                if iCont>aMax:break
                time.sleep(aMax)
            else:                
                self.Redis=None
                iRet=True
                break


    @property
    def REDISIp(self):return self._REDISIp
    @REDISIp.setter
    def REDISIp(self,aValue):self._REDISIp=aValue
    @property
    def REDISPort(self):return self._REDISPort
    @REDISPort.setter
    def REDISPort(self,aValue):self._REDISPort=aValue
    @property
    def REDISPassword(self):return self._REDISPassword
    @REDISPassword.setter
    def REDISPassword(self,aValue):self._REDISPassword=aValue
    @property
    def REDISCaCerts(self):return self._REDISCaCerts
    @REDISCaCerts.setter
    def REDISCaCerts(self,aValue):self._REDISCaCerts=aValue
    @property
    def REDISDb(self):return self._REDISDb
    @REDISDb.setter
    def REDISDb(self,aValue):self._REDISDb=aValue
    @property
    def Redis(self):
        if self._Redis==None:
            try:
                iPass=None
                if self.REDISPassword!="":iPass=self.REDISPassword
                iSsl=False
                iCa=None
                if os.path.exists(self.REDISCaCerts):
                    iSsl=True
                    iCa=self.REDISCaCerts
                self._Redis=redis.StrictRedis(host=self.REDISIp, port=self.REDISPort,password=iPass,ssl=False,ssl_ca_certs=iCa,db=self.REDISDb)
            except Exception as E:
                iError = "red2ws.Redis(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info())) + " (" + self.REDISIp + ":" + str(self.REDISPort) + ")"
                self.Logger.error(iError )    
                self._Redis=None
        return self._Redis
    @property
    def RedisWriter(self):
        if self._RedisWriter==None:
            try:
                iPass=None
                if self.REDISPassword!="":iPass=self.REDISPassword
                iSsl=False
                iCa=None
                if os.path.exists(self.REDISCaCerts):
                    iSsl=True
                    iCa=self.REDISCaCerts
                self._RedisWriter=redis.StrictRedis(host=self.REDISIp, port=self.REDISPort,password=iPass,ssl=False,ssl_ca_certs=iCa,db=self.REDISDb)
            except Exception as E:
                iError = "red2ws.Redis(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info())) + " (" + self.REDISIp + ":" + str(self.REDISPort) + ")"
                self.Logger.error(iError )    
                self._RedisWriter=None
        return self._RedisWriter
    @RedisWriter.setter
    def RedisWriter(self,aValue):self._RedisWriter=aValue
    def __init__(self,aHost="0.0.0.0",aPort=8080,aUrl=r'/(.+)',aRedisIp="127.0.0.1",aRedisPort=7001,aSslCertFile="",aSslKeyFile="",aRedisPassword="",aREDISCaCerts="",aRedisDb=0,aDebug=False):
        self._App=None
        self._LocalIp=None
        self._Url=None
        self._Client=None
        self._ClientSubs=None
        self._REDISPubSub=None
        self._Logger=None
        self._LogFileName=None
        self._Debug=aDebug
        self._WebSockets=[]
        self._Th=None
        self._Port=aPort
        self._Host=aHost
        self._REDISPort=aRedisPort
        self._REDISPassword=aRedisPassword
        self._REDISCaCerts=aREDISCaCerts
        self._Url=aUrl
        self._REDISIp=aRedisIp
        self._REDISPort=aRedisPort
        self._Redis=None
        self._RedisWriter=None
        self._SslCertFile=aSslCertFile
        self._SslKeyFile=aSslKeyFile
        self._REDISDb=aRedisDb
        


    
def GetParams():
    iParser = argparse.ArgumentParser("WebSocket Server Redis")
    iParser.add_argument("--websockport",type=int,help="WebSocket Port",default=8080)
    iParser.add_argument("--websockhost",type=str,help="WebSocket Host",default="0.0.0.0")
    iParser.add_argument("--websockurl",type=str,help="WebSocket Url",default=r'/(.+)')
    iParser.add_argument("--websocksslcertfile",type=str,help="ssl cert file for a wss:// protocol",default="")
    iParser.add_argument("--websocksslkeyfile",type=str,help="ssl key file for a wss:// protocol",default="")
    iParser.add_argument("--redishost",type=str,help="Redis Host",default="127.0.0.1")
    iParser.add_argument("--redisport",type=int,help="Redis Port",default=6379)
    iParser.add_argument("--redisdb",type=int,help="Redis db",default=0)
    iParser.add_argument("--redispassword",type=str,help="Redis password",default="")
    iParser.add_argument("--rediscacerts",type=str,help="Redis ca certs for ssl connections",default="")
    iParser.add_argument("--debug",type=int,help="Debug",default=0)
    return iParser.parse_args()
def Main():
    iObj=None
    try:
        iParams=GetParams()
        iObj=red2ws(iParams.websockhost,iParams.websockport,iParams.websockurl,iParams.redishost,iParams.redisport,iParams.websocksslcertfile,iParams.websocksslkeyfile,iParams.redispassword,iParams.rediscacerts,iParams.redisdb,iParams.debug==1)
        iObj.Start()
    except KeyboardInterrupt as Ke:
        pass
    except Exception as E:
        iError = "MAIN(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info()))
        iError=iError.replace("\n"," ")
        iObj.Logger.error(iError)
    finally:
        if iObj!=None:
            iObj.Stop()

if __name__ == "__main__":
    Main()
    
