## Setup


## Devlog

命令行窗口一：
```
cd ~

brew install python
sudo pip install --upgrade pip
sudo pip install pyspider
sudo pip install --allow-all-external mysql-connector-python
sudo pip install --allow-external mysql-connector-python mysql-connector-python

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





