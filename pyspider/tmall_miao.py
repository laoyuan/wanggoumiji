#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *

from datetime import datetime, timedelta
from pyquery import PyQuery
from HTMLParser import HTMLParser
import json, re, urlparse, demjson

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

    # on_start 不支持动态
    @every(minutes=60)
    def on_start(self):
        self.crawl('://', callback=self.miao_index, age=60, auto_recrawl=True, force_update=True)


    # 动态抓秒杀商品页面，从来没抓过的
    def miao_index(self, response): 
        items = db_tmall.select('select id, itemId, noItem from `tmall_items` where crawled_at=0 limit 0,100')
        for item in items:
            url_item = 'http://miao.item.taobao.com/' + item['itemId'] + '.htm'
            self.crawl(url_item, callback=self.miao_page, age=600, force_update=True, max_redirects=10, save=item)


    # 抓秒杀商品页面，如果商品不存在 noItem + 1
    @catch_status_code_error
    def miao_page(self, response):
        id = response.save['id']
        datetime_now = datetime.now()

        # 是秒杀
        if response.url == response.orig_url:
            json_text = fn_cut('g_config.idata=', '})();', response.text).strip()
            if json_text:
                json_data = demjson.decode(json_text)
                if json_data:
                    auctionStatus = int(json_data['item']['status'])
                    itemNum = int(response.doc('#J_SpanStock').text())
                    itemSecKillPrice = int(float(response.doc('#J_tkaPrice').attr('data-val')) * 100)
                    userId = json_data['seller']['id']
                    itemTitle = json_data['item']['title']
                    itemImg = response.doc('#J_ImgBooth').attr('data-src')
                    time_seckill = int(int(json_data['item']['dbst']) / 1000)
                    secKillTime = datetime.utcfromtimestamp(time_seckill) + timedelta(hours = 8) if time_seckill else 0
                    json_text = json.dumps(json_data)

                    item = {
                        'auctionStatus': auctionStatus,
                        'itemNum': itemNum,
                        'itemSecKillPrice': itemSecKillPrice, 
                        'userId': userId, 
                        'itemTitle': itemTitle,
                        'itemImg': itemImg, 
                        'secKillTime': secKillTime,
                        'crawled_at': datetime_now, 
                        'updated_at': datetime_now, 
                        'json_text': json_text, 
                    }


                    print item

                    n_update = db_tmall.update_where('tmall_items', item, id=id)
                    if n_update == 0:
                        print 'item update fail'

        #不是秒杀
        else:
            json_text = fn_cut('TShop.Setup(', '  );', response.text).strip()
            if json_text:
                json_data = json.loads(json_text)
                if json_data and 'itemDO' in json_data:
                    auctionStatus = int(json_data['itemDO']['auctionStatus'])
                    itemNum = int(json_data['itemDO']['quantity'])
                    itemTagPrice = int(float(json_data['itemDO']['reservePrice']) * 100)
                    userId = json_data['itemDO']['userId']
                    itemTitle = json_data['itemDO']['title']
                    itemImg = response.doc('#J_ImgBooth').attr.src

                    url_start = 'https:' + json_data['apiBidCount']
                    url_p = urlparse.urlparse(url_start)
                    query = urlparse.parse_qs(url_p.query)
                    time_start = int(int(query['date'][0]) / 1000) if 'date' in query else 0
                    startTime = datetime.utcfromtimestamp(time_start) + timedelta(hours = 8) if time_start else 0

                    json_text = json_text

                    item = {
                        'auctionStatus': auctionStatus,
                        'itemNum': itemNum,
                        'itemTagPrice': itemTagPrice, 
                        'userId': userId, 
                        'itemTitle': itemTitle,
                        'itemImg': itemImg, 
                        'startTime': startTime,
                        'crawled_at': datetime_now, 
                        'updated_at': datetime_now, 
                        'json_text': json_text, 
                    }

                    print item

                    n_update = db_tmall.update_where('tmall_items', item, id=id)
                    if n_update == 0:
                        print 'item update fail'

            else:
                if response.doc('.errorDetail h2') and response.doc('.errorDetail h2').text() == u'很抱歉，您查看的商品找不到了！':
                    noItem = response.save['noItem'] + 1
                    update_item = {
                        'noItem': noItem, 
                        'crawled_at': datetime_now, 
                        'updated_at': datetime_now, 
                    }

                    n_update = db_tmall.update_where('tmall_items', update_item, id=id)

                    print 'item no', id, noItem

                else:
                    print 'item fail', id, response.status_code, len(response.content), response.url



def fn_cut(start, end, s):
    if not (isinstance(s, str) or isinstance(s, unicode)):
        return ''

    p1 = 0 if start == '' else s.find(start)
    if p1 == -1:
        return ''
    e1 = p1 + len(start)

    if end == '':
        return s[e1:]

    p2 = s.find(end, e1)
    return s[e1:] if p2 == -1 else s[e1: p2]




