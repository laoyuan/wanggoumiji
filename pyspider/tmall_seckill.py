#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2015-04-29 16:20:11
# Project: s5

from pyspider.libs.base_handler import *
from datetime import datetime
import json

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
        url_index = 'https://www.tmall.com/wow/act/14700/yifenmiao'
        print url_index
        self.crawl(url_index, callback=self.index_page, age=300, priority=15, auto_recrawl=True, force_update=True, save={'id_act': 'www.tmall.com/wow/act/14700/yifenmiao'})

    @catch_status_code_error
    def index_page(self, response):
        datetime_now = datetime.now()
        ar_m = re.finditer(u'(www\.tmall\.com/wow/act/(.+?))\?', response.text.replace('&#x2F;', '/'))
        ar_act = {}
        for m in ar_m:
            ar_act[m.group(1)] = m.group(1)
        for act in ar_act:
            act_item = {'id_act': act, 'created_on': datetime_now}
            n_insert = q2.insert('tmall_act', **act_item)
            self.crawl('https://' + act, callback=self.index_page, age=600, priority=14, save=act_item)
            self.crawl('https://' + act + '?spm=', callback=self.index_page, age=600, priority=14, save=act_item, headers={'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'})

        if response.doc('.J_data'):
            ar_item = {'has_j': 1}
            n = q2.update_where('tmall_act', ar_item, id_act=response.save['id_act'])
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
    'brandLogo': each_item['brandLogo'], 'itemImg': each_item['itemImg'], 'id_act': response.save['id_act'], 'created_on': datetime_now}
                            n_insert = q2.insert('tmall_miaosha', **ar_item)
