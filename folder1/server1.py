import socket
import os
import subprocess
import datetime
import re
import hashlib


def findhashedvalue(filename):
    ans=hashlib.md5(filename).hexdigest()
    p='ls -l --full-time'+" "+filename
    output = subprocess.check_output(p, shell=True)
    output=output.split()
    ans=ans+" "+output[5]+" "+output[6]
    return ans

port = 60001
s = socket.socket()
host = ""

s.bind((host, port))
serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('', serverPort))
s.listen(5)

# filename = raw_input("Enter file to share:")
print 'Server listening....'
# print 'Got connection from', addr
while True:
    conn, addr = s.accept()
    data = conn.recv(1024)
    print('Server received', repr(data))
    a=data.split()
    if len(a)>=2:
        if a[0]=='permissions':
            output=str(os.stat(a[1]).st_mode & 0777)
            conn.send(output)
            conn.close()

        elif a[0]=='index':
            if a[1]=='list':
                command='ls -l'
                command=command+" "+a[2]
                output = subprocess.check_output(command, shell=True)
                output=output.split()
                print output
                ans=output[8]+" "+output[4]+" "+output[5]+" "+output[6]+" "+output[7]
                print ans
                conn.send(ans)
                conn.close()
                print 'Done sending'
            elif a[1]=='longlist':
                output = subprocess.check_output('ls -l', shell=True)
                output=output.split('\n')
                a=''
                for i in range(0,len(output)-1):
                    a=a+output[i]+'\n'
                a=a+output[len(output)-1]
                conn.send(a)
                conn.close()
                print('Done sending')
            elif a[1]=='shortlist':
                output = subprocess.check_output('ls -l --full-time', shell=True)
                output=output.split('\n')
                starttime=a[2]+" "+a[3]
                endtime=a[4]+" "+a[5]
                starttime=datetime.datetime.strptime(starttime,'%Y-%m-%d %X')
                endtime=datetime.datetime.strptime(endtime,'%Y-%m-%d %X')
                ans=''
                for i in range(1,len(output)-1):
                    b=output[i].split()
                    w=b[6].split(':')
                    z=w[2].split('.')
                    q=b[5]+" "+w[0]+":"+w[1]+":"+z[0]
                    ob=datetime.datetime.strptime(q,'%Y-%m-%d %X')
                    if starttime <= ob and ob<=endtime:
                        ans=ans+output[i]+'\n'
                conn.send(ans)
                conn.close()
                print('Done sending')
            elif a[1]=='regex':
                output = subprocess.check_output('ls -l', shell=True)
                output=output.split('\n')
                ans=''
                for i in range(1,len(output)-1):
                    b=output[i].split()
                    if re.match(a[2],b[8]) !=None:
                        ans=ans+b[8]+'\n'
                conn.send(ans)
                conn.close()
                print 'Done sending'
        elif a[0]=='hash':
            if a[1]=='verify':
                filename=a[2]
                ans=findhashedvalue(filename)
                conn.send(ans)
                conn.close()
                print 'Done sending'
            elif a[1]=='checkall':
                output = subprocess.check_output('ls -l', shell=True)
                output=output.split('\n')
                ans=''
                for  i in range(1,len(output)-1):
                    b=output[i].split()
                    ans=ans+b[8]+" "+findhashedvalue(b[8])+'\n'
                conn.send(ans)
                conn.close()
                print 'Done sending'
        elif a[0]=='download':
            if a[1]=='TCP':
                filename=a[2]
                f=open(filename,'rb')
                l=f.read(1024)
                while l:
                    conn.send(l)
                    l=f.read(1024)
                f.close()
                conn.close()
                print 'Done sending'
            elif a[1]=='UDP':
                filename=a[2]
                conn.close()
                print "The server is ready to receive"
            	message, clientAddress = serverSocket.recvfrom(2048)
                if message=="harsha":
                    print "yes"
                f=open(filename,'rb')
                l=f.read(2048)
                while l:
                    serverSocket.sendto(l, clientAddress)
                    l=f.read(2048)
                serverSocket.sendto(l, clientAddress)
                f.close()
