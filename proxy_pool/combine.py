#! /usr/bin/env python
# -*- coding: utf-8 -*-

read=open('proxylist.txt','rb')
proxy=eval(read.readline())
read.close()

for i in proxy:
    i['ip_port']=i.pop('HTTP')
    i['user_pass']=''

file=open('settinglist.txt','wb')
file.write(str(proxy))
file.close()