#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *

from datetime import datetime, timedelta
from pyquery import PyQuery
from HTMLParser import HTMLParser
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
        self.crawl('://', callback=self.shop_index, age=60, auto_recrawl=True, force_update=True)


    # 动态抓店铺，没有 userId 的
    def shop_index(self, response): 
        shops = db_tmall.select('select id, subdomain, type, noShop from `tmall_shops` where type>0 and userId=? and noShop<? limit 0,100', '', 3)
        for shop in shops:
            url_shop = 'https://' + shop['subdomain'] + '.tmall.com'
            self.crawl(url_shop, callback=self.shop_page, age=600, force_update=True, max_redirects=10, save=shop)


    # 抓天猫店铺首页抽取数据，如果店铺不存在 noShop + 1
    @catch_status_code_error
    def shop_page(self, response):
        id = response.save['id']
        datetime_now = datetime.now()

        # userID
        userId = fn_cut('sellerId: "', '"', response.text)

        if userId != '':

            # shopID
            shopId = fn_cut('shopId: "', '"', response.text)
            # wtId 不知道干什么用的
            wtId = fn_cut('wtId: "', '"', response.text)
            # 店铺用户名
            shopName = response.doc('.slogo-shopname').text()
            # 店铺完整域名
            url_p = urlparse.urlparse(response.url)
            shopDomain = url_p.hostname
            # userRate 评价页链接参数
            userRate = fn_cut('user-rate-', '.', response.doc('#dsr-ratelink').val())
            # xid 执照页链接参数
            datalazyload = PyQuery(response.doc('.ks-datalazyload').html())
            if datalazyload('.tm-gsLink').attr.href:
                url_zhao = 'http:' + datalazyload('.tm-gsLink').attr.href
                url_p = urlparse.urlparse(url_zhao)
                query = urlparse.parse_qs(url_p.query)
                xid = query['xid'][0] if 'xid' in query else ''
            else:
                xid = ''
            # shopAge 开店年数
            shopAge = datalazyload('.tm-shop-age-num').text() if datalazyload('.tm-shop-age-num') else '0'
            # city 所在地
            city = datalazyload('li.locus .right').text()
            # 评分、偏移量
            score = [0, 0, 0]
            offset = [0, 0, 0]
            i = 0
            for li in datalazyload('.shop-rate li').items():
                score[i] = int(float(li('.count').attr.title.replace(u'分', '')) * 100000)
                if li('b.fair'):
                    offset[i] = 0
                elif li('b.lower'):
                    offset[i] = - int(float(li('.rateinfo em').text().replace('%', '')) * 100)
                else:
                    offset[i] = int(float(li('.rateinfo em').text().replace('%', '')) * 100)
                i += 1
                if i == 3:
                    break

            shop_item = {
                'noShop': 0,
                'userId': userId, 
                'shopId': shopId, 
                'wtId': wtId,
                'shopName': shopName, 
                'shopDomain': shopDomain, 
                'userRate': userRate,
                'xid': xid,
                'shopAge': shopAge,
                'city': city,
                'score1': score[0],
                'score2': score[1],
                'score3': score[2],
                'offset1': offset[0],
                'offset2': offset[1],
                'offset3': offset[2],
                'updated_at': datetime_now, 
            }

            print 'shop OK', shop_item

            n_update = db_tmall.update_where('tmall_shops', shop_item, id=id)
            if n_update == 0:
                print 'shop update fail'

        else:
            if response.doc('.error-notice-hd') and response.doc('.error-notice-hd').text() == u'没有找到相应的店铺信息':
                noShop = response.save['noShop'] + 1
                update_item = {
                    'noShop': noShop, 
                    'updated_at': datetime_now, 
                }

                n_update = db_tmall.update_where('tmall_shops', update_item, id=id)

                print 'shop no', response.save['subdomain'], noShop

            else:
                print 'shop fail', id, response.status_code, len(response.content), response.url


        # 抽取页面内所有活动页 campaign 入库, type = 3

        html_text = HTMLParser().unescape(response.text)
        all_campaign = {}

        matches = re.finditer(u'([a-z0-9]+)\.tmall\.(com|hk)/campaign\-([a-zA-Z0-9_\-\.]+)', html_text)
        for m in matches:
            subdomain = m.group(1)
            campaign = subdomain + '.tmall.com/campaign-' + m.group(3)

            all_campaign[campaign] = campaign

        for campaign in all_campaign:
            campaign_item = {
                'campaign': campaign, 
                'type': 3,
                'item_num': 0,
                'subdomain': subdomain, 
                'crawled_at': 0,
                'created_at': datetime_now, 
                'updated_at': datetime_now, 
            }
            n_insert = db_tmall.insert('tmall_campaigns', **campaign_item)
        

        # 抽取页面所有商品入库，type = 3

        all_item = {}
        matches = re.finditer(u'detail\.tmall\.(com|hk)/([a-zA-Z0-9_\-\.\?&=]+)', html_text)
        for m in matches:
            url_p = urlparse.urlparse('http:' + m.group(0))
            query = urlparse.parse_qs(url_p.query)
            if 'id' in query:
                itemId = query['id'][0]
                all_item[itemId] = itemId

        for itemId in all_item:
            item = {
                'itemId': itemId, 
                'type': 3,
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

        print all_campaign
        print all_item



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





