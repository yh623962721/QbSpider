import sys, os
sys.path.append(os.path.abspath("../../"))
from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.utils.misc import load_object
from scrapy.spiders import Spider
from QbSpider.utils.RedisUtil import RedisConfUtil as rcu
DEFAULT_START_URLS_BATCH_SIZE = 16
DEFAULT_START_QUEUE_KEY = "%(spider)s:requests"
DEFAULT_START_QUEUE_CLASS="scrapy_redis.queue.SpiderPriorityQueue"
class RedisSpider(Spider):
    """Spider that reads urls from redis queue when idle."""
    redis_batch_size=None
    #ReHttpStatus_Code = [302, 500, 502, 503, 504, 408]

    def setup_redis(self, crawler=None):
        if crawler is None:
            # We allow optional crawler argument to keep backwards
            # compatibility.
            # XXX: Raise a deprecation warning.
            crawler = getattr(self, 'crawler', None)

        if crawler is None:
            raise ValueError("crawler is required")

        crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)
        settings = crawler.settings
        self.server = rcu().get_redis()
        self.queue_key=settings.get("SCHEDULER_QUEUE_KEY",DEFAULT_START_QUEUE_KEY)
        self.queue_cls=settings.get("SCHEDULER_QUEUE_CLASS",DEFAULT_START_QUEUE_CLASS)

        try:
            self.queue = load_object(self.queue_cls)(
                server=self.server,
                spider=self,
                key=self.queue_key % {'spider': self.name},
                serializer=None,
            )
        except TypeError as e:
            raise ValueError("Failed to instantiate queue class '%s': %s",
                             self.queue_cls, e)

        if self.redis_batch_size is None:
            self.redis_batch_size = settings.getint(
                'REDIS_START_URLS_BATCH_SIZE', DEFAULT_START_URLS_BATCH_SIZE,
            )

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(RedisSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.setup_redis(crawler)
        return obj


    def next_requests(self):
        """Returns a request to be scheduled or none."""
        # XXX: Do we need to use a timeout here?
        found = 0
        #if "rank" in self.queue_key:
        while found < self.redis_batch_size:
            req = self.queue.pop(0)
            # Queue empty
            if not req:
                break
            yield req
            found += 1
        if found:
            self.logger.debug("Read %s requests from '%s'", found, self.name)
    def schedule_next_requests(self):
        for req in self.next_requests():
            self.crawler.engine.crawl(req, spider=self)

    def spider_idle(self):
        print "$"*66
        self.schedule_next_requests()
        raise DontCloseSpider