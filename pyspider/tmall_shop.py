#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2015-04-29 16:20:11
# Project: s5

from pyspider.libs.base_handler import *
from transwarp import q2
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
        ar_act = ['muyin', 'food', 'ghjqyr']
        for act in ar_act:
            url_act = 'https://www.tmall.com/wow/act/14700/' + act
            self.crawl(url_act, fetch_type='js', callback=self.act_page, age=3600, priority=15, auto_recrawl=True, force_update=True)
        self.crawl('', callback=self.shop_index, age=600, auto_recrawl=True, force_update=True)

    @catch_status_code_error
    def act_page(self, response):
        ar_m = re.finditer(u'//(([^/]+?)\.tmall\.(com|hk)/campaign-[^\.]+\.htm)', response.text)
        for m in ar_m:
            sub = m.group(2).split('.')[0]
            tld = m.group(3)
            ar = q2.select_one('select * from `tmall_shops` where sub = ?', sub)
            if not ar:
                ar_shop = {'sub': sub, 'tld': tld}
                n_insert = q2.insert('tmall_shops', **ar_shop)
                ar = q2.select_one('select * from `tmall_shops` where sub = ?', sub)

            #所有正常商品
            url_list = 'https://' + sub + '.tmall.' + tld + '/search.htm?pageNo=1&search=y&tsearch=y'
            self.crawl(url_list, fetch_type='js', callback=self.list_page, age=1800, priority=10, save=ar)


        """
        ar = q2.select('select * from `tmall_shops` order by id desc')
        for i in range(len(ar)):
            url_list = 'https://' + ar[i]['sub'] + '.tmall.' + ar[i]['tld'] + '/search.htm?search=y&pageNo=1&tsearch=y'
            self.crawl(url_list, fetch_type='js', callback=self.list_page, age=1800, priority=10, save=ar[i])
            url_shop = 'https://' + ar[i]['sub'] + '.tmall.' + ar[i]['tld']
            self.crawl(url_shop, fetch_type='js', callback=self.index_page, age=1800, priority=5, save=ar[i])
        """

    #商品列表页
    @catch_status_code_error
    def list_page(self, response):
        if not response.save['userId']:
            json_str = fn_cut('window.shop_config = ', '};', response.text) + '}'
            json_data = json_decode(json_str)
            if json_data and 'userId' in json_data and json_data['userId']:
                shop_info = {'userId': json_data['userId']}
                if 'shopId' in json_data and json_data['shopId']:
                    shop_info['shopId'] = json_data['shopId']
                if 'siteId' in json_data and json_data['siteId']:
                    shop_info['siteId'] = json_data['siteId']
                if 'user_nick' in json_data and json_data['user_nick']:
                    shop_info['user_nick'] = urllib.unquote(json_data['user_nick'].encode('utf8'))
                if 'template' in json_data and 'id' in json_data['template'] and json_data['template']['id']:
                    shop_info['templateId'] = json_data['template']['id']
                response.save['userId'] = json_data['userId']
                q2.update_where('tmall_shops', shop_info, id=response.save['id'])

        if response.save['userId']:
            url_p = urlparse.urlparse(response.orig_url)
            query = urlparse.parse_qs(url_p.query)
            page = query['pageNo'][0] if 'pageNo' in query else 0
            for each_item in response.doc('.J_TItems .item-name').items():
                if each_item.attr.href:
                    url_p = urlparse.urlparse(each_item.attr.href)
                    query = urlparse.parse_qs(url_p.query)
                    if url_p.path == '/item.htm' and 'id' in query:
                        print query['id'][0]
                        ar_product = {'id': query['id'][0], 'userId': response.save['userId'], 'type': 1, 'page': page}
                        n_insert = q2.insert('tmall_products', **ar_product)

        for each_item in response.doc('.J_SearchAsync').items():
            url_p = urlparse.urlparse(each_item.attr.href)
            url_new = 'https://' + sort_query(url_p, remove='spm').replace('#anchor', '')
            self.crawl(url_new, fetch_type='js', callback=self.list_page, age=1800, priority=10, save=response.save)




        
