#encoding=utf8
import redis
import logging
logger = logging.getLogger(__name__)
REDIS_PARAMSS = {
'REDIS_HOST':'127.0.0.1',
#'REDIS_HOST':'61.164.149.156',
#'REDIS_HOST':'192.168.0.16',
'REDIS_PORT':6379,
#'REDIS_PASSWORD':"sy_wprjtr1yr4mr"
'REDIS_PASSWORD':'Qbbigdata'
}
'''
获取配置的工具类
'''
class RedisConfUtil():

    def get_redis(self):

        settings = REDIS_PARAMSS

        con = redis.Redis(host=settings["REDIS_HOST"],port=settings["REDIS_PORT"],password=settings["REDIS_PASSWORD"])

        #con = redis.Redis(host=settings["REDIS_HOST"], port=settings["REDIS_PORT"])

        logging.info(msg="Connect redis server success")

        return con











