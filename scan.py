#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

USAGE = """This is s special daemon used for checking whether the IP proxy works.
It can be managed by supervisor or some other tools, just make sure it works
all the time."""

import urllib
import urllib2
import httplib
import threading
import pymongo
import time
import sys
import os

from optparse import OptionParser

SETTING = {
        "SERVER":"localhost",
        "PORT":27017,
}

class IPPool(object):
    def __init__(self, server, port,  src_path, dst_path):
        connection = pymongo.MongoClient(server, port)
        self.src_collection = self._get_collection_by_path(connection, src_path)
        self.dst_collection = self._get_collection_by_path(connection, dst_path)

    def _get_collection_by_path(self, client, path):
        collection = client
        for node in path.split('.'):
            collection = getattr(collection, node)

        return collection

    def check_one(self, handler, url):
        res = self.src_collection.find_one_and_delete({})

        if res is None:
            time.sleep(360)
            return

        print "%s %s:%s, try to check" % (res["protocol"], res["ip"],
                res["port"])

        # Delete existed one
        self.dst_collection.delete_many(
                {"ip":res["ip"], "port":res["port"],
                "protocol":res["protocol"]})

        ret = handler(res["ip"], res["port"], res["protocol"], url)

        if ret:
            print "IP %s:%s good" % (res["ip"], res["port"])
            self.dst_collection.insert({"ip":res["ip"], "port":res["port"],
                "protocol":res["protocol"]})

    def get_one(self):
        return self.dst_collection.find_one()

    def get_all_iter(self):
        return self.dst_collection.find()


def proxy_test(ip, port='80', protocol='http', url='http://www.baidu.com'):
    proxy_url = protocol + '://' + ip + ':' + port
    proxy_support = urllib2.ProxyHandler({'http':proxy_url})
    opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
    request = urllib2.Request(url)
    request.add_header("Accept-Language", "zh-cn")
    request.add_header("Content-Type", "text/html; charset=gb2312")
    request.add_header("User-Agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)")

    trycount = 1
    while trycount <= 2:
        try:
            f = opener.open(request, timeout=3.0)
            data = f.read()
            if 'baidu.com' in data:
                break
            else:
                return False
        except:
            time.sleep(3)
            trycount = trycount + 1

    if trycount > 2:
        return False

    return True


class CheckTask(threading.Thread):
    def __init__(self, pool, handler, url):
        threading.Thread.__init__(self)
        self.pool = pool
        self.handler = handler
        self.url = url


    def run(self):
        while 1:
            self.pool.check_one(self.handler, url)


class ClickTask(threading.Thread):
    def __init__(self, pool, handler, url):
        threading.Thread.__init__(self)
        self.pool = pool
        self.handler = handler
        self.url = url


    def run(self):
        while 1:
            for res in self.pool.get_all_iter():
                self.handler(res["ip"], res["port"], res["protocol"], self.url)
                print "Click %s by %s" % (self.url, res["ip"])



if __name__ == "__main__":
    pool1 = IPPool(SETTING["SERVER"], SETTING["PORT"],
            "proxy.unchecked", "proxy.checked")
    pool2 = IPPool(SETTING["SERVER"], SETTING["PORT"],
            "proxy.checked", "proxy.checked")

    parser = OptionParser(usage=USAGE,
            version='0.0.1')

    parser.add_option("-n", "--number", dest="number",
            default='20', metavar='NUMBER',
            help="The number of threads used to scan.")

    parser.add_option("-u", "--url", dest="url",
            default='http://www.baidu.com', metavar='URL',
            help="The url to used to scan.")

    parser.add_option("-c", "--click", dest="click",
            default=False, action="store_true",
            help="Click url by proxy IP")


    (options, args) = parser.parse_args()

    thread_number = int(options.number)
    print "Thread number is %d + %d" % (thread_number, 1)
    url = options.url

    if options.click:
        tasktype =ClickTask
    else:
        tasktype =CheckTask

    tasks = []

    for i in range(thread_number):
        tasks.append(tasktype(pool1, proxy_test, url))

    tasks.append(tasktype(pool2, proxy_test, url))

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()
