import random
import base64
from settings import PROXIES
from scrapy import log
from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware

class RandomUserAgent(object):
    """Randomly rotate user agents based on a list of predefined ones"""

    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        #print "**************************" + random.choice(self.agents)
        request.headers.setdefault('User-Agent', random.choice(self.agents))

class ProxyMiddleware(object):
    def process_request(self, request, spider):
        proxy = random.choice(PROXIES)
        if proxy['user_pass'] is not None:
            request.meta['proxy'] = "http://%s" % proxy['ip_port']
            encoded_user_pass = base64.encodestring(proxy['user_pass'])
            request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
            print "**************ProxyMiddleware have pass************" + proxy['ip_port']
        else:
            print "**************ProxyMiddleware no pass************" + proxy['ip_port']
            request.meta['proxy'] = "http://%s" % proxy['ip_port']


class RetryRecordMiddleware(RetryMiddleware):

    def __init__(self, settings):
        RetryMiddleware.__init__(self, settings)

    def record_failed(self, path, request, exception, failed_meta):
        retries = request.meta.get('retry_times', 0) + 1
        log.msg('retries time is %s %d' % (retries, retries))
        log.msg('max_retry_times is %d' % self.max_retry_times)
        if retries > self.max_retry_times:
            failed_list = request.meta.get(failed_meta, [])
            failed_list = [x.strip() for x in failed_list]
            log.msg('recording failed list %s' % '\t'.join(failed_list))
            of = open(path, 'a')
            of.write('%s\n' % '\t'.join(failed_list))
            of.close()

    def process_exception(self, request, exception, spider):
        to_return = RetryMiddleware.process_exception(
            self, request, exception, spider)
        # customize retry middleware by modifying this
        request.meta['url'] = request.url
        record_failed('failed.txt', request, exception, 'url')
        return to_return