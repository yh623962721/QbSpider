#!/usr/bin/env python
# coding:utf-8

import requests
from hashlib import md5


class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id, con, jobid):
        self.username = username
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }
        self.con = con
        self.jobid = jobid
        self.items = []

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        try:
            r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        except Exception,e:
            import logging
            logging.warning(msg="Connect chaojiying server failed")
            self.items.append({"status":3})
            self.con.hmset(self.jobid, *self.items)
            return {u'pic_str':''}
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://code.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


# if __name__ == '__main__':
#     chaojiying = Chaojiying_Client('821907280', 'zqp821907280', 'soft_id')
#     im = open('a.jpg', 'rb').read()
#     print chaojiying.PostPic(im, 1004)['err_str']

