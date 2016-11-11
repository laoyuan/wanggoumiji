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
        url_index = 'https://1111.tmall.com/?wh_act_nativebar=2&wh_main=true'
        # pass to next mathod

        self.crawl(url_index, callback=self.index_page, age=1200, auto_recrawl=True, force_update=True)


    @catch_status_code_error
    def index_page(self, response):
        if response.status_code == 304 and response.error == 'HTTP 304: Not Modified':
            print 'act 304: Not Modified'
            return

        all_act = {}
        all_shop = {}
        all_campaign = {}
        all_item = {}
        datetime_now = datetime.now()

        # unescape html entity
        html_text = HTMLParser().unescape(response.text)

        # 抓取页面内所有会场

        matches = re.finditer(u'pages.tmall\.com/wow/act/16495/[a-zA-Z0-9_\-\.]+', html_text)
        for m in matches:
            all_act[m.group(0)] = m.group(0)

        for act_url in all_act:
            self.crawl('https://' + act_url, callback=self.index_page, age=1800)


        # 抽取页面内所有店铺 shop、活动页 campaign, type = 8

        matches = re.finditer(u'([a-z0-9]+)\.tmall\.(com|hk)/campaign\-([a-zA-Z0-9_\-\.]+)', html_text)
        for m in matches:
            subdomain = m.group(1)
            campaign = subdomain + '.tmall.com/campaign-' + m.group(3)

            all_shop[subdomain] = subdomain
            all_campaign[campaign] = campaign

        for subdomain in all_shop:
            shop_item = {
                'subdomain': subdomain, 
                'type': 8,
                'userId': '', 
                'shopId': '', 
                'wtId': '',
                'shopName': '', 
                'shopDomain': '', 
                'userRate': '',
                'xid': '',
                'shopAge': '',
                'city': '',
                'score1': 0,
                'score2': 0,
                'score3': 0,
                'offset1': 0,
                'offset2': 0,
                'offset3': 0,
                'crawled_at': 0,
                'created_at': datetime_now, 
                'updated_at': datetime_now, 
            }

            n_insert = db_tmall.insert('tmall_shops', **shop_item)
            n_update = db_tmall.update('update `tmall_shops` set type=8 where subdomain=? and type<8', subdomain)

        for campaign in all_campaign:
            campaign_item = {
                'campaign': campaign, 
                'type': 8,
                'item_num': 0,
                'subdomain': subdomain, 
                'crawled_at': 0,
                'created_at': datetime_now, 
                'updated_at': datetime_now, 
            }

            n_insert = db_tmall.insert('tmall_campaigns', **campaign_item)
        

        # 抽取页面内所有商品，type = 8

        matches = re.finditer(u'detail\.tmall\.(com|hk)/([a-zA-Z0-9_\-\.\?&=]+)', html_text)
        for m in matches:
            url_p = urlparse.urlparse('http:' + m.group(0))
            query = urlparse.parse_qs(url_p.query)
            if 'id' in query:
                itemId = query['id'][0]
                all_item[itemId] = itemId

        # 当前会场页数据入库

        act_url = response.orig_url
        title = response.doc('title').text().replace(u'-上天猫，就够了', '')
        act_num = len(all_act)
        campaign_num = len(all_campaign)
        shop_num = len(all_shop)
        item_num = len(all_item)

        act_item = {
            'act_url': act_url, 
            'title': title,
            'act_num': act_num,
            'campaign_num': campaign_num,
            'shop_num': shop_num,
            'item_num': item_num,
            'crawled_at': datetime_now,
            'created_at': datetime_now, 
            'updated_at': datetime_now, 
        }

        update_item = {
            'act_num': act_num,
            'campaign_num': campaign_num,
            'shop_num': shop_num,
            'item_num': item_num,
            'crawled_at': datetime_now,
        }

        n_update = db_tmall.update_where('tmall_acts', {'crawled_at': datetime_now}, act_url=act_url)
        if n_update == 0:
            n_insert = db_tmall.insert('tmall_acts', **act_item)

        select_item = db_tmall.select_one('select id from `tmall_acts` where act_url=?', act_url)
        act_id = select_item['id'] if 'id' in select_item else 0


        # 从会场抽取秒杀商品，type = 9 模式 1
        if response.doc('.zebra-act-ms-240x240'):
            n = db_tmall.update_where('tmall_acts', {'has_seckill': 1, 'updated_at': datetime_now}, act_url=act_url)

            seckill_data = response.doc('.zebra-act-ms-240x240').attr('data-config')
            all_seckill = json.loads(seckill_data)

            for each_group in all_seckill:
                if 'items' in each_group:
                    for each_item in each_group['items']:

                        miaosha_time = each_item['secKillTime'] if 'secKillTime' in each_item else ''
                        url_p = urlparse.urlparse('http:' + each_item['itemUrl'])
                        query = urlparse.parse_qs(url_p.query)
                        if 'id' in query:
                            itemId = query['id'][0]

                        if itemId:
                            print itemId
                            item = {
                                'itemId': itemId, 
                                'type': 9,
                                'itemTitle': each_item['itemTitle'], 
                                'secKillTime': miaosha_time, 
                                'itemNum': each_item['itemNum'].replace(',', ''), 
                                'itemSecKillPrice': int(float(each_item['itemSecKillPrice']) * 100), 
                                'itemTagPrice': int(float(each_item['itemTagPrice']) * 100), 
                                'itemImg': each_item['itemImg'],
                                'shop_id': 0, 
                                'act_id': act_id, 
                                'crawled_at': 0,
                                'created_at': datetime_now, 
                                'updated_at': datetime_now,
                            }
                            n_insert = db_tmall.insert('tmall_items', **item)
                            if n_insert == 0:
                                item.pop('created_at')
                                n_update = db_tmall.update_where('tmall_items', item, itemId=itemId)

        print act_item



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

