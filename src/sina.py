#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Long Changjin
# 
# Author:     Long Changjin <admin@longchangjin.cn>
# Maintainer: Long Changjin <admin@longchangjin.cn>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import ConfigParser
from xdg import BaseDirectory
from os.path import exists
from os import mkdir
import urlparse
import pycurl
import StringIO
import urllib
import json

from utils import parser_json

config_dir = BaseDirectory.xdg_config_home
APP_NAME = 'deepin-weibo'
WEIBO_CONFIG = "%s/%s/%s" % (config_dir, APP_NAME, 'sina.ini')

if not exists("%s/%s" % (config_dir, APP_NAME)):
    mkdir("%s/%s" % (config_dir, APP_NAME))
if not exists(WEIBO_CONFIG):
    open(WEIBO_CONFIG, 'wb').close()

class WeiboConfig():
    '''Weibo config'''
    def __init__(self, section, config_file=WEIBO_CONFIG):
        '''
        init config
        @param config_file: the file to save config
        '''
        self.config = ConfigParser.ConfigParser()
        self.config_file = config_file
        self.config.read(config_file)
        self.section = section

    def get(self, opt=None):
        if not self.config.has_section(self.section):
            return None
        if opt:
            return self.config.get(self.section, opt) if self.config.has_option(self.section, opt) else None
        back = {}
        for option in self.config.options(self.section):
            back[option] = self.config.get(self.section, option)
        return back

    def set(self, **kw):
        if not self.config.has_section(self.section):
            self.config.add_section(self.section)
        for option in kw:
            self.config.set(self.section, option, kw[option])
        self.config.write(open(self.config_file, 'wb'))
    
class Curl(object):
    METHOD_GET = 0
    METHOD_POST = 1
    METHOD_UPLOAD = 2

    def request(self, url, data=None, header=None, method=METHOD_GET, proxy_host=None, proxy_port=None):
        '''
        open url width get method
        @param url: the url to visit
        @param data: the data to post
        @param header: the http header
        @param proxy_host: the proxy host name
        @param proxy_port: the proxy port
        '''
        crl = pycurl.Curl()
        #crl.setopt(pycurl.VERBOSE,1)
        crl.setopt(pycurl.NOSIGNAL, 1)

        # set proxy
        if proxy_host:
            crl.setopt(pycurl.PROXY, proxy_host)
        if proxy_port:
            crl.setopt(pycurl.PROXYPORT, proxy_port)
        # set ssl
        crl.setopt(pycurl.SSL_VERIFYPEER, 0)
        crl.setopt(pycurl.SSL_VERIFYHOST, 0)
        crl.setopt(pycurl.SSLVERSION, 3)
         
        crl.setopt(pycurl.CONNECTTIMEOUT, 10)
        crl.setopt(pycurl.TIMEOUT, 300)
        crl.setopt(pycurl.HTTPPROXYTUNNEL, 1)

        if header:
            crl.setopt(pycurl.HTTPHEADER, header)

        crl.fp = StringIO.StringIO()
         
        if isinstance(url, unicode):
            url = str(url)
        if method == self.METHOD_POST and data is not None:
            crl.setopt(pycurl.POSTFIELDS, urllib.urlencode(data))  # post data
        elif method == self.METHOD_UPLOAD and data is not None:
            if type(data) == dict:
                upload_data = []
                for k in data:
                    upload_data.append((k, data[k]))
            else:
                upload_data = data
            crl.setopt(pycurl.HTTPPOST, upload_data)   # upload file
        crl.setopt(pycurl.URL, url)
        crl.setopt(crl.WRITEFUNCTION, crl.fp.write)
        try:
            crl.perform()
        except Exception:
            return None
        crl.close()
        back = crl.fp.getvalue()
        crl.fp.close()
        return back

class Sina(object):
    ''' '''
    def __init__(self):
        super(Sina, self).__init__()
        self.cfg = WeiboConfig('Sina')
        self.ACCESS_TOKEN = self.cfg.get('access_token')
        self.curl = Curl()
        self.code = None

        # 根据自己的app相应修改
        self.APP_KEY = '3703706716'
        self.APP_SECRET = 'c0ecbf8644ac043070449ad0901692b8'
        self.CALLBACK_URL = 'http://www.linuxdeepin.com'

        version = 2
        self.BASE_URL = 'https://api.weibo.com'
        self.API_BASE_URL = '%s/%d' % (self.BASE_URL, version)
        self.ACCESS_URL = '%s/oauth2/authorize?client_id=%s&redirect_uri=%s&display=popup&forcelogin=true' % (self.BASE_URL, self.APP_KEY,self.CALLBACK_URL)
        self.OAUTH2_URL = '%s/oauth2/access_token' % self.API_BASE_URL
        self.sina_url = 'http://www.weibo.com'

    def parse_code(self, callback):
        if not callback.startswith('http'):
            self.code = callback
            return self.code
        u = urlparse.urlparse(callback)
        query = urlparse.parse_qs(u.query, True)
        if 'code' in query and query['code']:
            self.code = query['code'][0]
        else:
            self.code = None
        return self.code

    def access_token(self, callback):
        if not self.parse_code(callback):
            return
        url = '%s?client_id=%s&client_secret=%s&grant_type=authorization_code&code=%s&redirect_uri=%s' % (
            self.OAUTH2_URL, self.APP_KEY, self.APP_SECRET, self.code, self.CALLBACK_URL)
        backjs = self.curl.request(url, [], method=self.curl.METHOD_POST)
        if backjs is None:
            return False
        try:
            back = json.loads(backjs)
        except:
            return False
        #print back
        if 'access_token' in back:
            self.cfg.set(**back)
            return True
        else:
            return False
        
    def __getattr__(self, attr):
        ''' __getattr__'''

        if attr.startswith("GET_"):
            api = attr[4:]
            method = Curl.METHOD_GET
        elif attr.startswith("POST_"):
            api = attr[5:]
            method = Curl.METHOD_POST
        elif attr.startswith("UPLOAD_"):
            api = attr[7:]
            method = Curl.METHOD_UPLOAD
        else:
            return None
        api = api.replace("__", '/')
        url = "%s/%s.json" % (self.API_BASE_URL, api)

        def wrap(*ka, **kw):
            kw.update({'access_token': self.ACCESS_TOKEN})
            if method == Curl.METHOD_GET:
                api_url = url + '?'
                for k in kw:
                    api_url = "%s%s=%s&" % (api_url, k, kw[k])
            else:
                api_url = url
            return parser_json(self.curl.request(api_url, kw, method=method))
        return wrap

if __name__ == '__main__':
    import webbrowser
    s = Sina()
    if not s.ACCESS_TOKEN:
        # 首先获取用户授权
        # 1.打开授权网页
        webbrowser.open(s.ACCESS_URL)
        # 2.输入授权后返回的URL或者code值
        # 如：http://www.linuxdeepin.com/?code=db3eb4e78fefe029b538f606bb0bd091 或者db3eb4e78fefe029b538f606bb0bd091
        callback_url = raw_input()
        s.access_token(callback_url)
    
    # http://open.weibo.com/wiki/API文档_V2
    # api格式为HTTP请求方式再加接口名，其中'/'使用'__'代替
    # 如：statuses/user_timeline接口为GET方式，则对应方法为：
    print s.GET_statuses__user_timeline(count=100, page=1)
    # statuses/destroy接口为POST方式，所需参数id
    # s.POST_statuses__destroy(id=3517990765424415)
    # statuses/upload接口为POST，但是需要上传文件，所以使用UPLOAD。所需参数status、pic
    # s.UPLOAD_statuses__upload(status="vim键盘图", pic=(pycurl.FORM_FILE, "vim.png"))
