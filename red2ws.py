#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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
try:
    import simplejson as json
except ImportError:
    import json
#wscat -c wss://armariunificat.bcn.cat/SUBSCRIBE/BCN_6_AU0600010
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
class WSHandler(tornado.websocket.WebSocketHandler):
    @property
    def Parent(self):return self.application.Server
    @property
    def RemoteIp(self):return self.request.remote_ip
    @property
    def Id(self):return id(self)
    def open(self,aUrl):
        self.Parent.Logger.info("OPEN: " + aUrl)
        self.Key=aUrl.upper()
        self._Contador=0
        if self.Parent.Debug:self.Parent.Logger.debug("DEBUG: OPEN WS (" + str(self.Id) + ") from " + self.RemoteIp)
        self.Parent.WebSockets.append(self)      
        #Publish connection
        self.Parent.REDISPublish(self.Key + "_CLIENTCONNECT", 1)
        time.sleep(.5)
    def on_message(self, message):pass
    def on_close(self):
        self.Parent.Logger.info("CLOSE: " + self.Key)
        if self.Parent.Debug:self.Parent.Logger.debug("DEBUG: CLOSE WS (" + str(self.Id) + ") from " + self.RemoteIp)
        self.Parent.WebSockets.remove(self)
        #Publish desconexion
        self.Parent.REDISPublish(self.Key + "_CLIENTCONNECT", 0)
    def check_origin(self, origin):return True
    def Write(self,aMsg):
        iKey=""
        try:
            iObj=aMsg
            iKey=iObj["IdInstalacion"]+"_"+iObj["IdUbicacion"]+"_"+iObj["IdControlador"]
            iKey=iKey.upper()
            if iKey==self.Key:
                self._Contador=self._Contador+1
                self.write_message(iObj)
                if self.Parent.Debug and self._Contador % 100 ==0:
                    self.Parent.Logger.debug("DEBUG: PUBLISH WS (" + str(self.Id) + ") to " + self.RemoteIp + ": " + str(self._Contador))
        except Exception as E:
            iError = "WSHandler.Write(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info())) + " (" + iKey + ":" + json.dumps(aMsg) +  ")"
            self.Parent.Logger.error(iError ) 
class red2ws(object):
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
    def WebSockets(self):return self._WebSockets
    @WebSockets.setter
    def WebSockets(self,aValue):self._WebSockets=aValue
    @property
    def LocalIp(self):
        if self._LocalIp==None:self._LocalIp=socket.gethostbyname(socket.gethostname())
        return self._LocalIp
    @property
    def Pattern(self):
        if self._Pattern==None:self._Pattern=r'/ws'
        return self._Pattern
    @Pattern.setter
    def Pattern(self,aValue):self._Pattern=aValue
    @property
    def App(self):
        if self._App==None:
            self._App=tornado.web.Application([(self.Pattern, WSHandler),])
            self._App.Server=self
        return self._App
    @App.setter
    def App(self,aValue):self._App=aValue
    @property
    def Client(self):
        if self._Client==None:
            self._Client=tornado.httpserver.HTTPServer(self.App)
            self._Client.listen(self.Port,address=self.Host)
        return self._Client
    @Client.setter
    def Client(self,aValue):
        self._Client=aValue
    def REDISPublish(self,aChannel,aValue):
        try:
            self.REDISClientSubs.publish(aChannel,aValue)
            return True
        except Exception as E:
            iError = "red2ws.REDISPublish(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info())) + " (" + aChannel + ":" + str(aValue) + ")"
            self.Logger.error(iError )    
            return False
    @property
    def Port(self):return self._Port
    @Port.setter
    def Port(self,aValue):
        self._Port=aValue
        self.Reset()
    @property
    def Host(self):return self._Host
    @Host.setter
    def Host(self,aValue):
        self._Host=aValue
        self.Reset()
    def StartWs(self):
        iClient=self.Client
        tornado.ioloop.IOLoop.instance().start()
    def StopWs(self):
        tornado.ioloop.IOLoop.instance().stop()
        self.Client=None
    def StartREDIS(self):
        self._REDISRunning=True
        self._Th=threading.Thread(target = self.REDISLoop)
        self._Th.start()
    def StopREDIS(self):
        self._REDISRunning=False
        self._Th=None
    def Start(self):
        self.StartREDIS()
        self.StartWs()
    def Stop(self):
        self.StopWs()
        self.StopREDIS()
    def Write(self,aMsg):
        for iWs in self.WebSockets:
            iWs.Write(aMsg)
    def Reconnect(self,aMax=10):
        iRet=False
        iCont=1
        while 1:
            try:
                iCont=iCont+1
                self.REDISClient.ping()                
            except redis.ConnectionError as E:
                if iCont>aMax:break
                time.sleep(aMax)
            else:                
                self.REDISPubSub=None
                self.REDISClient=None
                iRet=True
                break
    def REDISLoop(self):
        iMsg=None
        while self._REDISRunning:
            time.sleep(0.001)
            try:
                iData=""
                iChannel=""
                iType=""
                iMsg=self.REDISPubSub.get_message(timeout=1)
                if iMsg:
                    iType=iMsg['type']
                    if iType=="message":
                        iChannel=iMsg['channel']          
                        iData=iMsg['data']          
                        if iChannel in self.REDISChannels:
                            iData=json.loads(iMsg['data'])
                            self.Write(iData)
            except redis.ConnectionError as E:
                iError=str(E) + ":" + " Listener " + str(nsCaptureException(sys.exc_info())) + " (" + str(self.REDISChannels) + ":" + str(iMsg)  + ")"
                self.Logger.error(iError)  
                if self.Reconnect()==False:raise Exception("Not Connected reconnect Fail")
            except Exception as E:
                iError = "red2ws.REDISLoop(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info())) + " (" + iType + ":" + iChannel + ":" + str(iData) + ")"
                self.Logger.error(iError )    
                self.ResetREDIS()
    def Reset(self):self.Client=None
    def ResetREDIS(self):
        self.REDISPubSub=None
        self.REDISClient=None
        self.REDISClientSubs=None
    @property
    def REDISIp(self):return self._REDISIp
    @REDISIp.setter
    def REDISIp(self,aValue):self._REDISIp=aValue
    @property
    def REDISPort(self):return self._REDISPort
    @REDISPort.setter
    def REDISPort(self,aValue):self._REDISPort=aValue
    @property
    def REDISChannels(self):return self._REDISChannels
    @REDISChannels.setter
    def REDISChannels(self,aValue):self._REDISChannels=aValue
    @property
    def REDISClient(self):
        if self._REDISClient==None:
            try:
                self._REDISClient=redis.StrictRedis(host=self.REDISIp, port=self.REDISPort)
            except Exception as E:
                iError = "red2ws.REDISClient(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info())) + " (" + self.REDISIp + ":" + str(self.REDISPort) + ")"
                self.Logger.error(iError )    
                self._REDISCLient=None
        return self._REDISClient
    @REDISClient.setter
    def REDISClient(self,aValue):self._REDISClient=aValue
    @property
    def REDISClientSubs(self):
        if self._REDISClientSubs==None:
            try:
                self._REDISClientSubs=redis.StrictRedis(host=self.REDISIp, port=self.REDISPort)
            except Exception as E:
                iError = "red2ws.REDISClientSubs(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info())) + " (" + self.REDISIp + ":" + str(self.REDISPort) + ")"
                self.Logger.error(iError )    
                self._REDISClientSubs=None
        return self._REDISClientSubs
    @REDISClientSubs.setter
    def REDISClientSubs(self,aValue):self._REDISClientSubs=aValue
    @property
    def REDISPubSub(self):
        if self._REDISPubSub==None:
            try:
                self._REDISPubSub=self.REDISClient.pubsub()
                iLst=self.REDISChannels.split(",")
                for i in iLst:
                    self._REDISPubSub.subscribe(i)
            except Exception as E:
                iError = "red2ws.REDISPubSub(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info())) + " (" + self.REDISChannels + ")"
                self.Logger.error(iError )    
                self._REDISCLient=None
        return self._REDISPubSub
    @REDISPubSub.setter
    def REDISPubSub(self,aValue):self._REDISPubSub=aValue
    def __init__(self,aHost="0.0.0.0",aPort=8000,aPattern=r'/SUBSCRIBE/(.+)',aRedisIp="127.0.0.1",aRedisPort=7001,aRedisChannels="BCN_6_AU0600010",aDebug=False):
        self._App=None
        self._LocalIp=None
        self._Pattern=None
        self._Client=None
        self._ClientSubs=None
        self._REDISPubSub=None
        self._Logger=None
        self._LogFileName=None
        self._Debug=aDebug
        self._WebSockets=[]
        self._Th=None
        self._REDISRunning=False
        self._Port=aPort
        self._Host=aHost
        self._REDISPort=aRedisPort
        self._Pattern=aPattern
        self._REDISIp=aRedisIp
        self._REDISPort=aRedisPort
        self._REDISChannels=aRedisChannels
        self._REDISClient=None
        self._REDISClientSubs=None
def GetParams():
    iParser = argparse.ArgumentParser("WebSocket Server Redis")
    iParser.add_argument("--websockport",type=int,help="WebSocket Port",default=8000)
    iParser.add_argument("--websockhost",type=str,help="WebSocket Host",default="0.0.0.0")
    iParser.add_argument("--websockpattern",type=str,help="WebSocket Pattern",default=r'/SUBSCRIBE/(.+)')
    iParser.add_argument("--redishost",type=str,help="Redis Host",default="127.0.0.1")
    iParser.add_argument("--redisport",type=int,help="Redis Port",default=7001)
    iParser.add_argument("--redischannels",type=str,help="Redis Channels",default="BCN_6_AU0600010,BCN_6_AU0600020,BCN_6_AU0600030,BCN_6_AU0600040,BCN_6_AU0600050,BCN_10_AU1000070,BCN_2_AU0200060")
    iParser.add_argument("--debug",type=int,help="Debug",default=0)
    return iParser.parse_args()
def Main():
    try:
        iParams=GetParams()
        iObj=red2ws(iParams.websockhost,iParams.websockport,iParams.websockpattern,iParams.redishost,iParams.redisport,iParams.redischannels,iParams.debug==1)
        iObj.Start()
    except KeyboardInterrupt as Ke:
        pass
    except Exception as E:
        iError = "MAIN(): " + str(E) + ":" + str(nsCaptureException(sys.exc_info()))
        iError=iError.replace("\n"," ")
        iObj.Logger.error(iError)
        
    finally:
        iObj.Stop()
if __name__ == "__main__":Main()
    
