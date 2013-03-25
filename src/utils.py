#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2013 Deepin, Inc.
#               2011 ~ 2013 Hou ShaoHui
# 
# Author:     Hou ShaoHui <houshao55@gmail.com>
# Maintainer: Hou ShaoHui <houshao55@gmail.com>
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

import os
import time
from datetime import datetime
import dateutil
from dateutil import parser


try:
    import simplejson as json
except ImportError:    
    import json

    
def parser_json(raw):
    try:
        data = json.loads(raw)
    except:    
        try:
            data = eval(raw, type("Dummy", (dict,), dict(__getitem__=lambda s,n: n))())
        except:    
            data = {}
    return data    

def parse_datetime(strtime):
    dt = parser.parse(strtime)
    res = dt.astimezone(dateutil.tz.tzlocal())
    return datetime(*res.timetuple()[0:6])
    # try:
    #     return datetime(*datetime.strptime(strtime, '%a %b %d %H:%M:%S +0800 %Y')[0:6])
    # except:
    #     return datetime.now()

def parse_sina_datetime(strtime):
    sina_datetime  = parse_datetime(str(strtime))
    now = datetime.now()
    timedelta = now - sina_datetime    
    if timedelta.days > 0:
        return sina_datetime.strftime("%m月%d日 %H:%M")
    total_minutes = abs((now - sina_datetime).total_seconds()) / 60
    if total_minutes >= 60:
        return sina_datetime.strftime("今天 %H:%M")
    if total_minutes < 1: total_minutes = 1
    return "%d分钟前" % int(round(total_minutes))


def get_parent_dir(filepath, level=1):
    '''
    Get parent directory with given return level.
    
    @param filepath: Filepath.
    @param level: Return level, default is 1
    @return: Return parent directory with given return level. 
    '''
    parent_dir = os.path.realpath(filepath)
    
    while(level > 0):
        parent_dir = os.path.dirname(parent_dir)
        level -= 1
    
    return parent_dir
