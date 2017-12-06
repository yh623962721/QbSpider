# coding=utf-8
import sys, os
sys.path.append(os.path.abspath("../../"))
import json
import re

class Util(object):

    @staticmethod
    def obtain_json(resp_texts):
        '''
        format the response content
        '''
        #use regex for comm
        regex = "[\S\s]+?{([\S\s]+)}"
        resp_text = re.findall(re.compile(r'%s'%regex,re.I),resp_texts)
        if resp_text:
            return json.loads("{"+resp_text[0]+"}")
        else:
            return

    def check_contain_chinese(check_str):
        for ch in check_str.decode('utf-8'):
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

