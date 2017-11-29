import socket
import thread
#import urlparse
import select
import re
import codecs
from tld import get_tld
import requests
BUFLEN=8192

class Proxy(object):

    def __init__(self,conn,addr,rules):
        self.source=conn  # connect to the client
        self.request=""   # request part
        self.headers={}   # http headers
        self.destnation=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.rules = rules
        self.stop=False  
        self.run()  

    '''
    this function means to analysis http headers.
    '''
    def get_headers(self):
        header=''
        while True:
            header+= self.source.recv(BUFLEN)
            index=header.find('\n')
            if index >0:
                break
        firstLine = header[:index]
        self.request = header[index:]
        #host = self.request.strip().split("\n")[0][6:]
        host = re.findall(r'Host: (.*)',header[index:])[0].strip()
        self.headers['method'],self.headers['path'],self.headers['protocol']=firstLine.split()
        self.headers['host']=host
        domain = get_tld("http://"+host)
        if 'GET forbidden' in self.rules['request'] or "POST forbidden" in self.rules['request']:
                       self.stop=True
        if self.headers['path'] in self.rules['request']:
                       self.stop=True
        if domain in self.rules['whitelist']:
                       self.stop=False
        if domain in self.rules['blacklist']:
                       self.stop=True
        for i in self.rules['download']:
             if self.headers['path'].endswith(i):
                       self.stop=True
    '''
    this function means to transfer the requests to the host.
    '''
    def conn_destnation(self):
        hostname=self.headers['host']
        port="80"
        if hostname.find(':') >0:
            addr,port=hostname.split(':')
        else:
            addr=hostname
        port=int(port)
        ip=socket.gethostbyname(addr)
        if ip in self.rules['black_ip']:
             self.stop=True
             return
        print(ip,port)
        self.destnation.connect((ip,port))
        data="%s %s %s\r" %(self.headers['method'],self.headers['path'],self.headers['protocol'])
        self.destnation.send(data+self.request )
    '''
    this function means to transfer the data to the client.
    '''
    def renderto(self):
        readsocket=[self.destnation]
        while True:
            data=''
            (rlist,wlist,elist)=select.select(readsocket,[],[],3)
            if rlist:
                data=rlist[0].recv(BUFLEN)
                if len(data)>0:
                    self.source.send(data)
                else:
                    break

    def run(self):
        self.get_headers()
        if not self.stop:
           self.conn_destnation()
        if not self.stop:
           self.renderto()


GRAPH_SERVER='10.211.55.14'
class Server(object):

    def __init__(self,host,port,handler=Proxy):
        self.host=host
        self.port=port
        self.rules = {}
        self.server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host,port))
        self.server.listen(32)
        self.handler=handler

    def start(self):
        while True:
            try:
                conn,addr=self.server.accept()
                if addr[0]!=GRAPH_SERVER:
                   thread.start_new_thread(self.handler,(conn,addr,self.rules))
                else:
                   #TODO update the rules
                   print("pass")
                   pass
            except Exception as err:
                print(err)
                break

    def init_rules(self):
          # URL filters
          self.rules['blacklist']=['sjtu.edu.cn'] 
          self.rules['whitelist']=['baidu.com']
          self.rules['black_ip'] = []
          self.rules['white_ip'] = []
          # GET/POST/HEADER filters
          self.rules['request'] = []
          # applet\download word\ filters
          self.rules['response'] = []
          self.rules['download']=['.apk','.doc'] 
          #self.rules['request'].append("GET forbidden")
          self.rules['blacklist']= []
if __name__=='__main__':
    s=Server('',8080)  ## listening on port 8080
    s.init_rules()
    s.start()
