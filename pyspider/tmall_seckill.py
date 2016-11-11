#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-11-06 11:20:11
# Project: tmall_seckill

from pyspider.libs.base_handler import *
from datetime import datetime
from HTMLParser import HTMLParser
import json, re, urlparse

# 修改 db_tmall.py 最后一行连接数据库，每次修改需要重启 pyspider
import db_tmall


class Handler(BaseHandler):

    crawl_config = {
        'headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,fr;q=0.4',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
        },
        'timeout': 20,
    }

    @every(minutes=60)
    def on_start(self):

        # 总会场页
        url_index = 'https://1111.tmall.com/'
        self.crawl(url_index, callback=self.index_page, age=600, auto_recrawl=True, force_update=True)


    @catch_status_code_error
    def index_page(self, response):
        if response.status_code == 304 and response.error == 'HTTP 304: Not Modified':
            print 'act 304: Not Modified'
            return

        all_act = {}
        datetime_now = datetime.now()

        # unescape html entity
        html_text = HTMLParser().unescape(response.text)

        # 抓取页面内所有会场

        matches = re.finditer(u'pages.tmall\.com/wow/act/16495/[a-zA-Z0-9_\-\.]+', html_text)
        for m in matches:
            all_act[m.group(0)] = m.group(0)

        for act_url in all_act:
            self.crawl('https://' + act_url, callback=self.index_page, age=1200)


        # 当前会场页数据入库

        act_url = response.orig_url
        title = response.doc('title').text().replace(u'-上天猫，就够了', '')

        act_item = {
            'act_url': act_url, 
            'title': title,
            'crawled_at': datetime_now,
            'created_at': datetime_now, 
            'updated_at': datetime_now, 
        }

        update_item = {
            'crawled_at': datetime_now,
        }

        n_update = db_tmall.update_where('tmall_acts', {'crawled_at': datetime_now}, act_url=act_url)
        if n_update == 0:
            n_insert = db_tmall.insert('tmall_acts', **act_item)

        select_item = db_tmall.select_one('select id from `tmall_acts` where act_url=?', act_url)
        act_id = select_item['id'] if 'id' in select_item else 0


        # 从会场抽取秒杀商品，模式 1
        if response.doc('.zebra-act-ms-240x240'):
            n = db_tmall.update_where('tmall_acts', {'has_seckill': 1, 'updated_at': datetime_now}, act_url=act_url)

            seckill_data = response.doc('.zebra-act-ms-240x240').attr('data-config')
            if seckill_data:
                all_seckill = json.loads(seckill_data)
                if all_seckill:
                    for each_group in all_seckill:
                        if 'items' in each_group:
                            for each_item in each_group['items']:

                                url_p = urlparse.urlparse('http:' + each_item['itemUrl'])
                                query = urlparse.parse_qs(url_p.query)
                                if 'id' in query:
                                    itemId = query['id'][0]

                                    if itemId:
                                        print itemId

                                        itemTitle = each_item['itemTitle'] if 'itemTitle' in each_item else ''
                                        secKillTime = each_item['secKillTime'] if ('secKillTime' in each_item and each_item['secKillTime'].find(',') < 0) else 0
                                        itemNum = each_item['itemNum'].replace(',', '') if 'itemNum' in each_item else ''
                                        itemSecKillPrice = int(float(each_item['itemSecKillPrice'].replace(u'元', '')) * 100) if 'itemSecKillPrice' in each_item else 0
                                        itemImg = each_item['itemImg'] if 'itemImg' in each_item else ''

                                        item = {
                                            'itemId': itemId, 
                                            'type': 1,
                                            'itemTitle': itemTitle, 
                                            'secKillTime': secKillTime, 
                                            'itemNum': itemNum, 
                                            'itemSecKillPrice': itemSecKillPrice, 
                                            'itemTagPrice': 0, 
                                            'itemImg': itemImg,
                                            'shop_id': 0, 
                                            'act_id': act_id, 
                                            'userId': '',
                                            'crawled_at': 0,
                                            'created_at': datetime_now, 
                                            'updated_at': datetime_now,
                                        }
                                        n_insert = db_tmall.insert('tmall_items', **item)
                                        if n_insert == 0:
                                            item.pop('created_at')
                                            n_update = db_tmall.update_where('tmall_items', item, itemId=itemId)



       # 从会场抽取秒杀商品，模式 2
        if response.doc('.zebra-time-rush .J_dynamic_data'):
            n = db_tmall.update_where('tmall_acts', {'has_seckill': 2, 'updated_at': datetime_now}, act_url=act_url)

            seckill_data = response.doc('.zebra-time-rush .J_dynamic_data').text()
            if seckill_data:
                all_seckill = json.loads(seckill_data)

                if 'picList' in all_seckill:
                    for each_item in all_seckill['picList']:
                        url_p = urlparse.urlparse('http:' + each_item['itemUrl'])
                        query = urlparse.parse_qs(url_p.query)
                        if 'id' in query:
                            itemId = query['id'][0]

                            if itemId:
                                print itemId

                                item = {
                                    'itemId': itemId, 
                                    'type': 2,
                                    'itemTitle': '', 
                                    'secKillTime': 0, 
                                    'itemNum': 0, 
                                    'itemSecKillPrice': 0, 
                                    'itemTagPrice': 0, 
                                    'itemImg': '',
                                    'shop_id': 0, 
                                    'act_id': act_id, 
                                    'userId': '',
                                    'crawled_at': 0,
                                    'created_at': datetime_now, 
                                    'updated_at': datetime_now,
                                }
                                n_insert = db_tmall.insert('tmall_items', **item)
                                if n_insert == 0:
                                    item.pop('created_at')
                                    n_update = db_tmall.update_where('tmall_items', item, itemId=itemId)




