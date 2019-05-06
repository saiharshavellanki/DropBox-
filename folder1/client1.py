import socket
import os
import subprocess
import hashlib
import datetime
import time
import signal

automate=0
def handler(signum, frame):
    automate=0
    print 'Ctrl+Z pressed, but ignored'

host = ""
port = 60000
s=socket.socket()
def downloadfile(filename):
    s=socket.socket()
    s.connect((host, port))
    h="download TCP "+filename
    s.send(h)
    f=open(filename,'wb')
    while True:
        data=s.recv(1024)
        if not data:
            break
        f.write(data)
    f.close()
    s.close()

    s = socket.socket()
    s.connect((host,port))
    h="permissions "+filename
    s.send(h)
    data=s.recv(1024)
    s.close()
    if data=="Not valid":
        print "Not valid permissions"
    else:
        data=int(data)
        os.chmod(filename,data)

current_time=time.time()
update_time=time.time()
automate=0
while True:
    flag=0
    s = socket.socket()
    b=raw_input("prompt> ")
    a=b.split()
    logfile=open("client.log","a+")
    logfile.write(b+'\n')
    logfile.close()
    if len(a)==1 and a[0]=='automate':
        flag=1
        automate=1
    elif len(a)>=2:
        if a[0]=='index':
            s.connect((host, port))
            if a[1]=='longlist':
                flag=1
                h=a[0]+" "+a[1]
                s.send(h)
            elif a[1]=='shortlist':
                flag=1
                starttime=a[2]+" "+a[3]
                endtime=a[4]+" "+a[5]
                h=a[0]+" "+a[1]+" "+starttime+" "+endtime
                s.send(h)
            elif a[1]=='regex':
                flag=1
                h=a[0]+" "+a[1]+" "+a[2]
                s.send(h)
            if flag==1:
                data = s.recv(1024)
                print data
            s.close()

        elif a[0]=='hash':
            s.connect((host, port))
            if a[1]=='verify':
                flag=1
                h=a[0]+" "+a[1]+" "+a[2]
                s.send(h)
            elif a[1]=='checkall':
                flag=1
                h=a[0]+" "+a[1]
                s.send(h)
            if flag==1:
                data=s.recv(1024)
                print data
            s.close()

        elif a[0]=='download':
            if a[1]=='TCP':
                flag=1
                downloadfile(a[2])

                s=socket.socket()
                s.connect((host,port))
                data=s.recv(1024)
                s.close()
                if data=="Not valid":
                    print "Not valid"
                else:
                    s = socket.socket()
                    s.connect((host,port))
                    h="index list "+a[2]
                    s.send(h)
                    data=s.recv(1024)
                    s.close()

                    s=socket.socket()
                    s.connect((host,port))
                    h="hash verify "+a[2]
                    s.send(h)
                    data1=s.recv(1024)
                    data1=data1.split()
                    s.close()
                    print data,data1[0]

            elif a[1]=='UDP':
                flag=1
                s.connect((host,port))
                h="download UDP "+a[2]
                s.send(h)
                s.close()
                serverName = ''
                serverPort = 12001
                clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                message = "harsha"
                clientSocket.sendto(message,(serverName, serverPort))
                f=open(a[2],'wb')
                while True:
                    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
                    if not modifiedMessage:
                        break
                    f.write(modifiedMessage)
                f.close()
                clientSocket.close()

                s = socket.socket()
                s.connect((host,port))
                h="index list "+a[2]
                s.send(h)
                data=s.recv(1024)
                s.close()

                s = socket.socket()
                s.connect((host,port))
                h="hash verify "+a[2]
                s.send(h)
                data1=s.recv(1024)
                data1=data1.split()
                hashedvalue=hashlib.md5(a[2]).hexdigest()
                print data,data1[0]
                if data1[0]==hashedvalue:
                    print "File download success"
                else:
                    print "File download failed"
                s.close()
    if flag==0:
        print "Invalid command"
    while 1:
        current_time=time.time()
        if automate==0:
            break
        signal.signal(signal.SIGTSTP, handler)
        if automate==1 and current_time-update_time>5:
            flag=1
            s=socket.socket()
            update_time = current_time
            s.connect((host,port))
            s.send("hash checkall")
            server_files=s.recv(1024)
            s.close()

            server_files=server_files.split('\n')
            client_files_info = subprocess.check_output('ls -l --full-time', shell=True)
            client_files_info=client_files_info.split('\n')
            client_files=[]

            for i in range(1,len(client_files_info)-1):
                h=client_files_info[i]
                h=h.split()
                hashedvalue=hashlib.md5(h[8]).hexdigest()
                ans=h[8]+" "+hashedvalue+" "+h[5]+" "+h[6]
                client_files.append(ans)

            for i in range(0,len(server_files)):
                p=server_files[i]
                p=p.split()
                if len(p)!=0:
                    for j in range(0,len(client_files)):
                        q=client_files[j]
                        q=q.split()
                        # print p,q
                        a=p[3].split(':')
                        b=q[3].split(':')
                        ts=datetime.datetime.strptime(p[2]+" "+a[0]+" "+a[1],'%Y-%m-%d %H %M')
                        tc=datetime.datetime.strptime(q[2]+" "+b[0]+" "+b[1],'%Y-%m-%d %H %M')
                        count=0
                        if p[0]==q[0]:
                            count=1
                            if p[1]!=q[1] and ts>tc:
                                s=socket.socket()
                                downloadfile(p[0])
                    if count==0:
                        s=socket.socket()
                        downloadfile(p[0])
