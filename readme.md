## Setup
```

CREATE TABLE IF NOT EXISTS `tmall.tmall_acts` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `act_url` varchar(100) NOT NULL,
  `title` varchar(500) NOT NULL,
  `has_seckill` int(11) NOT NULL DEFAULT '0',
  `act_num` int(11) NOT NULL DEFAULT '0',
  `campaign_num` int(11) NOT NULL DEFAULT '0',
  `shop_num` int(11) NOT NULL DEFAULT '0',
  `item_num` int(11) NOT NULL DEFAULT '0',
  `crawled_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `act_url` (`act_url`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS `tmall.tmall_items` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `itemId` varchar(20) NOT NULL,
  `type` int(11) NOT NULL DEFAULT '0',
  `noItem` int(11) NOT NULL DEFAULT '0',
  `auctionStatus` int(11) NOT NULL DEFAULT '0',
  `itemNum` int(11) NOT NULL DEFAULT '0',
  `itemSecKillPrice` int(11) NOT NULL DEFAULT '0',
  `itemTagPrice` int(11) NOT NULL DEFAULT '0',
  `shop_id` int(11) NOT NULL DEFAULT '0',
  `act_id` int(11) NOT NULL DEFAULT '0',
  `userId` varchar(20) NOT NULL,
  `itemTitle` varchar(500) NOT NULL,
  `itemImg` varchar(1000) NOT NULL,
  `json_text` text NOT NULL,
  `startTime` timestamp NULL DEFAULT NULL,
  `secKillTime` timestamp NULL DEFAULT NULL,
  `crawled_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `itemId` (`itemId`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;

```

```
cd ~
git clone https://github.com/laoyuan/wanggoumiji.git
cd wanggoumiji/pyspider
pip install pyspider
pyspider
```

edit `db_tmall.py` to connect to your database

visit: `http://localhost:5000/`
make `tmall_seckill` and `tmall_miao` running


## Devlog

命令行窗口一：
```
cd ~

pip install pyspider

brew install python
pip install --upgrade pip
pip install pyspider
pip install --allow-all-external mysql-connector-python

# 安装 mysql.connector，pip 不支持了
git clone https://github.com/mysql/mysql-connector-python.git
cd mysql-connector-python
python ./setup.py build
sudo python ./setup.py install

cd ~
mkdir wgmj
cd wgmj
mkdir pyspider
cd pyspider
pyspider
```

在浏览器打开 http://localhost:5000/ 点 create，Project Name 填 tmall_seckill 点 create
弹出页面右面窗口改为 execfile('./tmall_seckill.py') 点 save

命令行窗口二：
```
cd ~/wgmj

vi .gitignore

git init
git remote add origin https://github.com/laoyuan/wanggoumiji.git
git add .
git commit -m "first"
git push origin master -u 
```





