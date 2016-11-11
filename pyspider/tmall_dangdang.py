#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *

from datetime import datetime, timedelta
from pyquery import PyQuery
from HTMLParser import HTMLParser
import json, re, urlparse, requests

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
        aId = '8de6bf29853b4bc49970b46321a2b0d7'
        self.crawl('https://dangdang.tmall.com/', callback=self.dangdang_index, age=60, force_update=True, max_redirects=10, save={'aId': aId})


    @catch_status_code_error
    def dangdang_index(self, response):
        aId = response.save['aId']

        if response.doc('.aQV8e-Lpgl'):
            url_coupon = 'https:' + response.doc('.aQV8e-Lpgl').attr.href
            url_p = urlparse.urlparse(url_coupon)
            query = urlparse.parse_qs(url_p.query)
            activityId = query['activityId'][0] if 'activityId' in query else ''
            print aId, activityId
            if activityId != '' and activityId != aId:
                url_message = 'http://localhost/price/api_dingsend.php?message=dangdang_new_activityId_' + activityId
                r = requests.get(url_message)
                print r.text
                aId = activityId

        self.crawl('https://dangdang.tmall.com/', callback=self.dangdang_index, age=60, force_update=True, max_redirects=10, save={'aId': aId})

            
            

  


