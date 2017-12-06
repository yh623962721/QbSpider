# -*- coding: utf-8 -*-
import os
import sys
import uuid
import traceback
from logging import exception


import time
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from QbSpider.hbases import Hbase
from QbSpider.hbases.ttypes import *
import json
from scrapy.utils.project import get_project_settings

sys.path.append(os.path.abspath("../"))
class HbClient(object):

    split_char = '\t'

    mapping = {
                u'联通-个人信息': ('yys_lt_cl', 'YYS_LT'),
                u'联通-登录记录': ('yys_lt_al', 'YYS_LT'),
                u'联通-通话详单': ('yys_lt_cd', 'YYS_LT'),
                u'联通-历史账单': ('yys_lt_hb', 'YYS_LT'),
                u'联通-账户余额': ('yys_lt_ab', 'YYS_LT'),
                u'联通-手机上网流量详单': ('yys_lt_cf', 'YYS_LT'),
                u'联通-增值业务详单': ('yys_lt_va', 'YYS_LT'),
                u'联通-积分查询': ('yys_lt_sq', 'YYS_LT'),
                u'联通-短彩信详单查询': ('yys_lt_sd', 'YYS_LT'),
                u'联通-沃家成员信息': ('yys_lt_gi', 'YYS_LT'),
                u'联通-手机上网记录': ('yys_lt_cnpr', 'YYS_LT'),
                u'联通-实时话费': ('yys_lt_rt', 'YYS_LT'),

                u"公积金-湖南-信息查询 ":('gjj_hunan_bs', 'GJJ_HUNAN'),
                u"公积金-湖南-明细查询 ":('gjj_hunan_dt', 'GJJ_HUNAN'),
                u"公积金-湖南-贷款信息查询 ":('gjj_hunan_la', 'GJJ_HUNAN'),
                u"公积金-湖南-信息查询":('gjj_bs', 'GJJ_HUNAN'),
                u"公积金-湖南-明细查询":('gjj_dt', 'GJJ_HUNAN'),
                u"公积金-湖南-贷款信息查询":('gjj_la', 'GJJ_HUNAN'),

                u"电信-江苏-个人信息": ('yys_dx_jiangsu_cl', 'YYS_DX_JIANGSU'),
                u"电信-江苏-积分查询":('yys_dx_jiangsu_sq', 'YYS_DX_JIANGSU'),
                u"电信-江苏-增值业务详单": ('yys_dx_jiangsu_va', 'YYS_DX_JIANGSU'),
                u"电信-江苏-套餐查询": ('yys_dx_jiangsu_pi', 'YYS_DX_JIANGSU'),
                u"电信-江苏-历史账单": ('yys_dx_jiangsu_hb', 'YYS_DX_JIANGSU'),
                u"电信-江苏-语音通话详单": ('yys_dx_jiangsu_cd', 'YYS_DX_JIANGSU'),
                u"电信-江苏-短彩信详单查询": ('yys_dx_jiangsu_sd', 'YYS_DX_JIANGSU'),
                u"电信-江苏-账户余额": ('yys_dx_jiangsu_ab', 'YYS_DX_JIANGSU'),

                u"电信-上海-个人信息": ('yys_dx_shanghai_cl', 'YYS_DX_SHANGHAI'),
                u"电信-上海-积分查询": ('yys_dx_shanghai_sq', 'YYS_DX_SHANGHAI'),
                u"电信-上海-增值业务详单": ('yys_dx_shanghai_va', 'YYS_DX_SHANGHAI'),
                u"电信-上海-套餐查询": ('yys_dx_shanghai_pi', 'YYS_DX_SHANGHAI'),
                u"电信-上海-历史账单": ('yys_dx_shanghai_hb', 'YYS_DX_SHANGHAI'),
                u"电信-上海-语音通话详单": ('yys_dx_shanghai_cd', 'YYS_DX_SHANGHAI'),
                u"电信-上海-短彩信详单查询": ('yys_dx_shanghai_sd', 'YYS_DX_SHANGHAI'),
                u"电信-上海-账户余额": ('yys_dx_shanghai_ab', 'YYS_DX_SHANGHAI'),

                u"支付宝-首页信息": ('alipay_hm', 'ZFB_ALIPAY'),
                u"支付宝-余额宝详细信息": ('alipay_yeb', 'ZFB_ALIPAY'),
                u"支付宝-实名账户查询": ('alipay_rn', 'ZFB_ALIPAY'),
                u"支付宝-银行卡信息": ('alipay_bc', 'ZFB_ALIPAY'),
                u"支付宝-账单信息": ('alipay_bill', 'ZFB_ALIPAY'),
                u"支付宝-个人基本信息": ('alipay_cl', 'ZFB_ALIPAY'),
                u"支付宝-地址信息": ('alipay_ad', 'ZFB_ALIPAY'),

              }

    def __init__(self, pageName='login_key_page', keysName='login_user_keys'):

        settings = get_project_settings().getdict('PARAMS_CONNECT_HBASE')

        self.keysName = keysName
        self.pageName = pageName
        self.host = settings['host']
        self.port = settings['port']
        self.buf = settings['buf']

        self.reversemapping = self.__reversemapping()

    def __open(self):
        self.transport = TTransport.TBufferedTransport(TSocket.TSocket(self.host, self.port), rbuf_size=self.buf)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Hbase.Client(self.protocol)
        self.transport.open()


    def __gentm(self):
        return str(int(time.time()))


    def __reversemapping(self):
        dic = {}
        for k in self.mapping:
            col, site = self.mapping[k]

            if site not in dic:
                dic[site] = {}

            if col in dic[site]:
                raise Exception('repeated columns %s' % col)

            dic[site][col] = k
        return dic

    def __insertpage(self, rowkey, url, html, struct_dic, row_key, post_dic=None, charset='utf-8'):

        if not html:
            return
        if struct_dic:
            alist = struct_dic[struct_dic.keys()[0]]
            if alist:
                for d in alist:
                    d['pagekey'] = rowkey
                    d['rowkey'] = row_key

        try:
            post_data = None
            if post_dic:
                post_data = json.dumps(post_dic)

            mutations = [Mutation(column="f:url", value=url),
                         Mutation(column="f:cnt", value=html),
                         Mutation(column="f:typ", value=charset),
                         Mutation(column="f:pst", value=post_data),
                         Mutation(column="f:tm", value=self.__gentm()),
                         Mutation(column="p:json", value=json.dumps(struct_dic))]
            self.client.mutateRow(self.pageName, rowkey, mutations, None)
        except Exception, e:
            print traceback.format_exc()
            print e.message
            print 'rowkey:', rowkey
            print 'data:', struct_dic

    def insert(self, colname, url, html, struct_dic, id, token, charset='utf-8',post_dic=None):

        colname, std = self.mapping.get(colname, ('', ''))
        row_std = std + '_%s_%s'
        value_std = std + '_%s_%s_%s'

        if not colname and not id and not token:
            raise exception('colname not exists')

        row_key = row_std % (id, token)

        value_key = value_std % (id, colname, uuid.uuid1().get_hex())
        value_key1 = value_key + self.split_char

        try:
            self.__open()
            col = 'c:%s' % colname
            append = TAppend(table=self.keysName, row=row_key, columns=[col], values=[value_key1])
            self.client.append(append)
            self.__insertpage(rowkey=value_key, url=url, html=html, struct_dic=struct_dic, row_key=row_key, post_dic=post_dic, charset=charset)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', value_key

    def selectasdict(self, rowkey):
        """
        return rowkey, dict
        """
        self.__open()
        trowresult = self.client.getRow(self.keysName, rowkey, None)
        if not trowresult:
            return rowkey, {}

        bigdic = {}
        # 取列名

        dic_col = trowresult[0].columns
        for col in dic_col:
            # 取列key
            arr = dic_col[col].value.strip().split(self.split_char)
            if not arr:
                continue

            if len(arr) == 1:
                pagekey = arr[0]
                presult = self.client.get(self.pageName, pagekey, 'p:json', None)
                if presult:
                    dic_11 = json.loads(presult[0].value)
                    bigdic[col] = dic_11
            else:
                dic_merged = {}
                k_1 = None
                for pkey in arr:
                    tmp = self.client.get(self.pageName, pkey, 'p:json', None)
                    if not tmp:
                        continue
                    tmp_dic = json.loads(tmp[0].value)
                    if not dic_merged:
                        dic_merged = tmp_dic
                        k_1 = dic_merged.keys()[0]
                    else:
                        dic_merged[k_1].extend(tmp_dic[k_1])
                bigdic[col] = dic_merged
        return rowkey, bigdic


    def select(self, rowkey):
        self.__open()
        trowresult = self.client.getRow(self.keysName, rowkey, None)
        if not trowresult:
            yield rowkey, None, None, None, None
        else:
            site = '_'.join(rowkey.split('_')[0: 2])
            rmap = self.reversemapping[site]

            dic_col = trowresult[0].columns
            for col in dic_col:
                arr = dic_col[col].value.strip().split(self.split_char)
                if not arr:
                    yield rowkey, col, None, None, rmap[col.split(':')[1]]
                else:
                    if len(arr) == 1:
                        pagekey = arr[0]
                        presult = self.client.get(self.pageName, pagekey, 'p:json', None)
                        if presult:
                            yield rowkey, col, presult[0].value, pagekey, rmap[col.split(':')[1]]
                        else:
                            yield rowkey, col, None, pagekey, rmap[col.split(':')[1]]
                    else:
                        dic_merged = {}
                        k_1 = None
                        for pkey in arr:
                            tmp = self.client.get(self.pageName, pkey, 'p:json', None)
                            if not tmp:
                                continue
                            if not dic_merged:
                                dic_merged = json.loads(tmp[0].value)
                                k_1 = dic_merged.keys()[0]
                            else:
                                dic_merged[k_1].extend(json.loads(tmp[0].value)[k_1])
                        yield rowkey, col, json.dumps(dic_merged), arr, rmap[col.split(':')[1]]


    def getrowkeys(self, prefix):

        def ftime(m):
            m = int(str(m)[0: -3])
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m))

        self.__open()
        rows = []
        id = self.client.scannerOpenWithPrefix(tableName=self.keysName, startAndPrefix=prefix, columns=[], attributes=None)
        while True:
            try:
                result = self.client.scannerGetList(id=id, nbRows=10)
            except:
                break
            if not result:
                break
            for e in result:
                columns = e.columns
                timestamp = None
                if columns:
                    timestamp = columns[columns.keys()[0]].timestamp
                    timestamp = ftime(timestamp)
                rows.append((e.row, timestamp))
        return rows

    def delrowsprefix(self, prefix):
        rows = self.getrowkeys(prefix)
        self.__open()
        for rowkey, _ in rows:
            self.client.deleteAllRow(self.keysName, row=rowkey, attributes=None)



class HbUnicom(object):
    """
    172.28.40.43:9090 thrift1
    """

    #def __init__(self, host='172.28.40.23', port=9090, tabName='login_key_page', mapName='login_user_keys'):
    #def __init__(self, host='172.28.40.45', port=9090, tabName='login_key_page', mapName='login_user_keys'):
    def __init__(self, host='172.28.40.43', port=9090, tabName='login_key_page', mapName='login_user_keys'):
        self.tabName = tabName
        self.mapName = mapName
        self.transport = TTransport.TBufferedTransport(TSocket.TSocket(host, port), rbuf_size=512)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Hbase.Client(self.protocol)
        # print self.client
        self.transport.open()
        #self.logger = logging.getLogger('spider')

    def __del__(self):
        self.transport.close()

    def __genkey(self, phone, url, post_data):
        if isinstance(post_data,int):
            post_data = str(post_data)
        row_key = '%s_%s' % (phone, url)
        if post_data:
            row_key += '_' + post_data
        return row_key

    def __inserttm(self, rowkey):
        mutations = [Mutation(column="c:yys_tm", value=self.__gentm())]
        self.client.mutateRow(self.mapName, rowkey, mutations, None)

    def __gentm(self):
        return str(int(time.time()))

    def insert_page(self, url, phone, html, charset, struct_json, post_data=None):
        """
        schema:
        f:url -> 网页地址
        f:cnt -> 网页
        f:typ -> 网页编码
        p:json -> 结构化数据json
        """
        try:
            row_key = self.__genkey(phone, url, post_data)
            mutations = [Mutation(column="f:url", value=url),
                         Mutation(column="f:cnt", value=html),
                         Mutation(column="f:typ", value=charset),
                         Mutation(column="f:tm", value=self.__gentm()),
                         Mutation(column="p:json", value=json.dumps(struct_json))]
            self.client.mutateRow(self.tabName, row_key, mutations, None)
        except Exception, e:
            print traceback.format_exc()
            print e.message
            print 'rowkey:', row_key
            print 'data:', struct_json

    def insert_person_info(self, phone, jobid, url, post_data=None):
        """
        用户信息:个人信息
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'
        try:
            append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_pi'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_bill_statis(self, phone, jobid, url, post_data=None):
        """
        账单查询:六个月的话费统计
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_bs'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_bill_detail(self, phone, jobid, url, post_data=None):
        """
        详单查询:
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_bd'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_account_info(self, phone, jobid, url, post_data=None):
        """
        账户信息：
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_ai'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_charge_detail(self, phone, jobid, url, post_data=None):
        """
        费用明细:
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_cd'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_remain_score(self, phone, jobid, url, post_data=None):
        """
        积分余额
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_rs'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_commu_amount(self, phone, jobid, url, post_data=None):
        """
        通信量
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_ca'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_account_detail(self, phone, jobid, url, post_data=None):
        """
        账户明细
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        try:
            append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_ad'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

    def insert_record_login(self, phone, jobid, url, post_data=None):
        """
        用户登录信息
        """
        row_key = 'YYS_LT_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        #data_key += '\ttest'
        data_key += '\t'
        #append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_ld'], values=[data_key])
        #self.client.append(append)
        try:
            append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_ld'], values=[data_key])
            self.client.append(append)
            self.__inserttm(row_key)
        except Exception, e:
            print traceback.format_exc()
            print e
            print e.message
            print 'rowkey:', row_key
            print 'data:', data_key

class HbTelecom(object):
    """
    172.28.40.43:9090 thrift1
    """

    def __init__(self, host='172.28.40.43', port=9090, tabName='login_key_page', mapName='login_user_keys'):
        self.tabName = tabName
        self.mapName = mapName
        self.transport = TTransport.TBufferedTransport(TSocket.TSocket(host, port), rbuf_size=512)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Hbase.Client(self.protocol)
        # print self.client
        self.transport.open()
        #self.logger = logging.getLogger('spider')

    def __del__(self):
        self.transport.close()

    def __genkey(self, phone, url, post_data):
        if isinstance(post_data,int):
            post_data = str(post_data)
        row_key = '%s_%s' % (phone, url)
        if post_data:
            row_key += '_' + post_data
        return row_key

    def __inserttm(self, rowkey):
        mutations = [Mutation(column="c:yys_tm", value=self.__gentm())]
        self.client.mutateRow(self.mapName, rowkey, mutations, None)

    def __gentm(self):
        return str(int(time.time()))

    def insert_page(self, url, phone, html, charset, struct_json, post_data=None):
        """
        schema:
        f:url -> 网页地址
        f:cnt -> 网页
        f:typ -> 网页编码
        p:json -> 结构化数据json
        """
        row_key = self.__genkey(phone, url, post_data)
        mutations = [Mutation(column="f:url", value=url),
                     Mutation(column="f:cnt", value=html),
                     Mutation(column="f:typ", value=charset),
                     Mutation(column="f:tm", value=self.__gentm()),
                     Mutation(column="p:json", value=json.dumps(struct_json))]
        self.client.mutateRow(self.tabName, row_key, mutations, None)

    def insert_person_info(self, phone, jobid, url, post_data=None):
        """
        用户信息:个人信息
        """
        row_key = 'YYS_DX_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_pi'], values=[data_key])
        self.client.append(append)
        self.__inserttm(row_key)

    def insert_bill_statis(self, phone, jobid, url, post_data=None):
        """
        账单查询:六个月的话费统计
        """
        row_key = 'YYS_DX_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_bs'], values=[data_key])
        self.client.append(append)
        self.__inserttm(row_key)

    def insert_bill_detail(self, phone, jobid, url, post_data=None):
        """
        详单查询:
        """
        row_key = 'YYS_DX_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_bd'], values=[data_key])
        self.client.append(append)
        self.__inserttm(row_key)

    def insert_account_info(self, phone, jobid, url, post_data=None):
        """
        账户信息：
        """
        row_key = 'YYS_DX_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_ai'], values=[data_key])
        self.client.append(append)
        self.__inserttm(row_key)

    def insert_charge_detail(self, phone, jobid, url, post_data=None):
        """
        费用明细:
        """
        row_key = 'YYS_DX_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_cd'], values=[data_key])
        self.client.append(append)
        self.__inserttm(row_key)

    def insert_remain_score(self, phone, jobid, url, post_data=None):
        """
        积分余额
        """
        row_key = 'YYS_DX_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_rs'], values=[data_key])
        self.client.append(append)
        self.__inserttm(row_key)

    def insert_commu_amount(self, phone, jobid, url, post_data=None):
        """
        通信量
        """
        row_key = 'YYS_DX_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_ca'], values=[data_key])
        self.client.append(append)
        self.__inserttm(row_key)

    def insert_account_detail(self, phone, jobid, url, post_data=None):
        """
        账户明细
        """
        row_key = 'YYS_DX_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_ad'], values=[data_key])
        self.client.append(append)
        self.__inserttm(row_key)

    def insert_record_login(self, phone, jobid, url, post_data=None):
        """
        用户登录信息
        """
        row_key = 'YYS_DX_%s_%s' % (phone, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(phone, url, post_data)
        data_key += '\t'

        append = TAppend(table=self.mapName, row=row_key, columns=['c:yys_ld'], values=[data_key])
        self.client.append(append)
        self.__inserttm(row_key)

class HbDZDP(object):
    """
    172.28.40.43:9090 thrift1
    """

    def __init__(self, host='172.28.40.23', port=9090, tabName='login_key_page', mapName='login_user_keys'):
        self.tabName = tabName
        self.mapName = mapName
        self.transport = TTransport.TBufferedTransport(TSocket.TSocket(host, port), rbuf_size=512)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = Hbase.Client(self.protocol)
        # print self.client
        self.transport.open()
        #self.logger = logging.getLogger('spider')

    def __del__(self):
        self.transport.close()

    def __genkey(self, shopid, url, post_data):
        if isinstance(post_data,int):
            post_data = str(post_data)
        row_key = '%s_%s' % (shopid, url)
        if post_data:
            row_key += '_' + post_data
        return row_key

    def __inserttm(self, rowkey):
        mutations = [Mutation(column="c:xmd_tm", value=self.__gentm())]
        self.client.mutateRow(self.mapName, rowkey, mutations, None)

    def __gentm(self):
        return str(int(time.time()))

    def insert_page(self, url, shopid, html, charset, struct_json, post_data=None):
        """
        schema:
        f:url -> 网页地址
        f:cnt -> 网页
        f:typ -> 网页编码
        p:json -> 结构化数据json
        """
        row_key = self.__genkey(shopid, url, post_data)
        mutations = [Mutation(column="f:url", value=url),
                     Mutation(column="f:cnt", value=html),
                     Mutation(column="f:typ", value=charset),
                     Mutation(column="f:tm", value=self.__gentm()),
                     Mutation(column="p:json", value=json.dumps(struct_json))]
        self.client.mutateRow(self.tabName, row_key, mutations, None)

    def insert_DZDP_review(self, shopid, jobid, url, post_data=None):
        """
        大众点评评论信息
        """
        #XMD_DZDP_shopID_token
        row_key = 'XMD_DZDP_%s_%s' % (shopid, jobid)
        # 这里要设置为全局变量
        data_key = self.__genkey(shopid, url, post_data)
        data_key += '\t'

        append = TAppend(table=self.mapName, row=row_key, columns=['c:xmd_cl', 'c:xmd_tm'], values=[data_key, str(int(time.time()))])
        self.client.append(append)
        #self.__inserttm(row_key)


if __name__ == '__main__':
    #hb = HbDZDP()
    #hb.insert_DZDP_review('100009', 'jobid00000001', 'www.dzdp.com')
    html = """
    <!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>hbase 查询工具</title>
</head>
<body>
    <table>
    <tr>
    <td>
    <form action="/search-post" method="post">
        {% csrf_token %}
        <input type="text" name="q" onFocus="this.value=''" style="width:400px">
        <input type="submit" value="查询">
    </form>
    </td>

    </tr>

    </table>
    <p>{{ rowkeys|safe }}</p>
    <p>{{ rlt|safe }}</p>
</body>
</html>

    """
    # from selenium import webdriver
    # sel = webdriver.PhantomJS(executable_path='D:\work_python\QbSpider\QbSpider\project_test\phantomjs.exe')
    # sel.maximize_window()
    # sel.get("D:\work_python\QbSpider\QbSpider\project_test\alipay_address_index.html")
    # sel.implicitly_wait(3)
    # html = sel.page_source
    # data = {}
    # data['alipay_asset_banklist'] =[{'bank_name': '', 'bank_num': '', 'express_status': '', 'card_type': '', 'pagekey': u'ZFB_ALIPAY_15921046604_alipay_bc_d872bc1ed4b011e7835db881985de273', 'rowkey': u'ZFB_ALIPAY_15921046604_ddddddddddddd1'}, {'bank_name': '', 'bank_num': '', 'express_status': '', 'card_type': '', 'pagekey': u'ZFB_ALIPAY_15921046604_alipay_bc_d872bc1ed4b011e7835db881985de273', 'rowkey': u'ZFB_ALIPAY_15921046604_ddddddddddddd1'}, {'bank_name': '', 'bank_num': '', 'express_status': '', 'card_type': '', 'pagekey': u'ZFB_ALIPAY_15921046604_alipay_bc_d872bc1ed4b011e7835db881985de273', 'rowkey': u'ZFB_ALIPAY_15921046604_ddddddddddddd1'}]
    # ALIPAY_ADDRESS_INDEX_URL = "https://memberprod.alipay.com/address/index.htm"
    # user = "15921046604"
    # token = "eeeeeeeeeeeee"
    # items = {}
    # items_count= {}
    # items_count["items"] = [items]

    hb = HbClient()
    # hb.insert(colname=u"支付宝-余额宝详细信息", url=ALIPAY_ADDRESS_INDEX_URL, html=html,
    #                struct_dic=data,
    #                id=user, post_dic={}, token=token)

    rows = hb.getrowkeys("")
    for row in rows:
        print row
        # for rowkey, col, res, arr, name in hb.select(row[0]):
        #     if res:
        #         res = json.loads(res)
        #         print res
