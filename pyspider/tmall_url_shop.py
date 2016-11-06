#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *
from datetime import datetime
import json, re, urlparse

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
        self.crawl('', callback=self.shop_index, age=30, auto_recrawl=True, force_update=True)

    # 动态抓没有 userId 的店铺
    @catch_status_code_error
    def shop_index(self, response): 
        ar = db_tmall.select('select * from `tmall_shop_url` where userId = ""')

        for i in range(len(ar)):
            self.crawl('http://' + ar[i]['sub'] + '.tmall.com', fetch_type='js', callback=self.shop_page, save=ar[i], priority=9, age=600, force_update=True)
        
    # 抓天猫店铺首页
    @catch_status_code_error
    def shop_page(self, response):
        sub = response.save['sub']
        shopID = fn_cut('shopId: "', '"', response.text)
        userID = fn_cut('sellerId: "', '"', response.text)
        if shopID != '':
            print sub, shopID
            shopName = response.doc('.slogo-shopname').text()
            url_p = urlparse.urlparse(response.url)
            shopDomain = url_p.hostname
            ar_item = {'shopID': shopID, 'userID': userID, 'shopName': shopName, 'shopDomain': shopDomain}
            n_update = db_tmall.update_where('tmall_shop_url', ar_item, sub=sub)
        else:
            print response.headers


def fn_cut(start, end, str):
    p1 = 0 if start == '' else str.find(start)
    if p1 == -1:
        return ''
    e1 = p1 + len(start)

    if end == '':
        return str[e1:]

    p2 = str.find(end, e1)
    return str[e1:] if p2 == -1 else str[e1: p2]





