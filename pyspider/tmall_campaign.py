#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *

from datetime import datetime, timedelta
from HTMLParser import HTMLParser
import re, urlparse

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
        'timeout': 20,
    }

    # on_start 不支持动态
    @every(minutes=60)
    def on_start(self):
        self.crawl('://', callback=self.campaign_index, age=60, auto_recrawl=True, force_update=True)


    # 动态抓campaign，6小时内没抓过的
    def campaign_index(self, response):
        time_renew = datetime.now() - timedelta(hours = 6)
        campaigns = db_tmall.select('select id, campaign from `tmall_campaigns` where type>0 and crawled_at<? limit 0,100', time_renew)
        for campaign in campaigns:
            url_campaign = 'https://' + campaign['campaign']
            self.crawl(url_campaign, callback=self.campaign_page, age=600, force_update=True, max_redirects=10, save=campaign)


    # 抓天猫店铺活动页抽取商品，type = 4
    @catch_status_code_error
    def campaign_page(self, response):
        id = response.save['id']
        datetime_now = datetime.now()

        html_text = HTMLParser().unescape(response.text)

        all_item = {}
        matches = re.finditer(u'detail\.tmall\.(com|hk)/([a-zA-Z0-9_\-\.\?&=]+)', html_text)
        for m in matches:
            url_p = urlparse.urlparse('http:' + m.group(0))
            query = urlparse.parse_qs(url_p.query)
            if 'id' in query:
                itemId = query['id'][0]
                all_item[itemId] = itemId
                item = {
                    'itemId': itemId, 
                    'type': 4,
                    'noItem': 0,
                    'itemNum': 0,
                    'itemSecKillPrice': 0,
                    'itemTagPrice': 0,
                    'shop_id': 0,
                    'act_id': 0,
                    'userId': '',
                    'itemTitle': '',
                    'itemImg': '',
                    'secKillTime': '',
                    'crawled_at': 0,
                    'created_at': datetime_now, 
                    'updated_at': datetime_now, 
                }

                n_insert = db_tmall.insert('tmall_items', **item)

        print all_item

        # 更新 campaign
        update_campaign = {
            'crawled_at': datetime_now,
            'item_num': len(all_item),
        }

        n_update = db_tmall.update_where('tmall_campaigns', update_campaign, id=id)
        if n_update == 0:
            print 'campaign update fail'





