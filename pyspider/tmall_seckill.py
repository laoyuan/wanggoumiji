#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-06 11:20:11
# Project: tmall_seckill

from pyspider.libs.base_handler import *
from datetime import datetime
import json
import re
# db_tmall.py 的最后一行连接数据库
import db_tmall



class Handler(BaseHandler):

    crawl_config = {
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,fr;q=0.4',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
        },
        'timeout': 100,
    }


    @every(minutes=60)
    def on_start(self):
        url_index = 'https://1111.tmall.com/?wh_act_nativebar=2&wh_main=true'
        id_act = '1111.tmall.com'
        # 会场入口页
        self.crawl(url_index, callback=self.index_page, age=600, priority=9, auto_recrawl=True, force_update=True, save={'id_act': id_act})


    @catch_status_code_error
    def index_page(self, response):

        # 当前会场页面存入数据库
        id_act_current = response.save['id_act']
        datetime_now = datetime.now()
        title = response.doc('title').text().replace(u'-上天猫，就够了', '')
        act_item = {'id_act': id_act_current, 'created_on': datetime_now, 'title': title}
        print act_item

        n_insert = db_tmall.insert('tmall_act', **act_item)

        # 采集页面内所有会场 url
        ar_act = {}
        ar_m = re.finditer(u'([a-z]+\.tmall\.com/wow/act/16495/(.+?))\?', response.text.replace('&#x2F;', '/'))
        for m in ar_m:
            ar_act[m.group(1)] = m.group(1)
        print ar_act

        for id_act in ar_act:
            if '"' in id_act:
                id_act = id_act[:id_act.find('"')]
            self.crawl('https://' + id_act, callback=self.index_page, age=1200, save={'id_act': id_act})

        # 秒杀商品，模式 1
        if 'data-mod-name="mui/zebra-act-ms-240x240/index-pc" data-config="' in response.text:
            n = db_tmall.update_where('tmall_act', {'has_seckill': 1}, id_act=id_act_current)

            json_data = json_decode(response.doc('.J_data').text())
            for j_item in json_data:
                if json_data and 'items' in j_item:
                    for each_item in j_item['items']:
                        itemId = each_item['itemId']
                        miaosha_time = each_item['belongTab'] if 'belongTab' in each_item else ''
                        if not itemId:
                            if each_item['itemUrl']:
                                url_p = urlparse.urlparse('http:' + each_item['itemUrl'])
                                query = urlparse.parse_qs(url_p.query)
                                if 'id' in query:
                                    itemId = query['id'][0]
                        if not itemId:
                            if each_item['itemUrlPc'] and 'campaign' in each_item['itemUrlPc']:
                                url_p = urlparse.urlparse('http:' + each_item['itemUrlPc'])
                                itemId = url_p.hostname + url_p.path + '?time=' + miaosha_time.replace(' ', '_')

                        if itemId:
                            print itemId
                            ar_item = {'itemId': itemId, 'itemTitle': each_item['itemTitle'], 
    'belongTab': miaosha_time, 'itemNum': each_item['itemNum'].replace(',', ''), 
    'itemSecKillPrice': each_item['itemSecKillPrice'], 'itemTagPrice': each_item['itemTagPrice'], 
    'brandLogo': each_item['brandLogo'], 'itemImg': each_item['itemImg'], 'id_act': id_act_current, 'created_on': datetime_now}
                            n_insert = db_tmall.insert('tmall_miaosha', **ar_item)



#解析json 字符串，is_jsonp 出去外包括号
def json_decode(json_str, is_jsonp=False):
    if is_jsonp and '(' in json_str:
        p_str = json_str[json_str.find('(') + 1:]
        if ')' in p_str:
            json_str = p_str[0: p_str.rfind(')')]
    try:
        return json.loads(json_str)
    except ValueError:
        return False

