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

import gtk
import cairo
import webkit
import webbrowser

import javascriptcore as jscore
from sina import Sina


class PopupWindow(gtk.Window):
    
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_colormap(gtk.gdk.Screen().get_rgba_colormap())
        self.set_size_request(300, 580)
        self.connect("destroy", gtk.main_quit)
        
        # self.connect("expose-event", self.on_expose_event)
        self.sina = Sina()
        
        self.webview = webkit.WebView()
        self.webview.set_transparent(True)
        self.webview.open("file:///home/evilbeast/project/web/weido/static/html/timeline.html")
        self.webview.connect('new-window-policy-decision-requested', self.navigation_request_cb)
        self.webview.connect('navigation-policy-decision-requested', self.navigation_request_cb)
        self.webview.connect("load-finished", lambda w, e: self.on_button_clicked(w))
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.add(self.webview)
        
        vbox = gtk.VBox()
        button = gtk.Button("更多")
        button.connect("clicked", self.on_button_clicked)
        vbox.pack_start(scrolled_window, True, True)
        vbox.pack_start(button, False, False)
        
        self.count = 20
        self.js_context = jscore.JSContext(self.webview.get_main_frame().get_global_context()).globalObject                
        self.add(vbox)
        self.show_all()
        gtk.main()
        
    def navigation_request_cb(self, view, frame, request, action, decision):
        """ Handle clicks on links, etc. """

        uri = request.get_uri()
        webbrowser.open(uri)
        return True
        
        
    def on_button_clicked(self, widget):    
        timeline = self.sina.GET_statuses__home_timeline(count=self.count, page=1)
        statuses = timeline.get("statuses", [])
        if len(statuses) > 0:
            self.js_context.hello(statuses)            
            self.count += 20
        
    def on_expose_event(self, widget, event):    
        cr  = widget.window.cairo_create()
        rect = widget.allocation
        
        # Clear color to transparent window.
        if self.is_composited():
            cr.rectangle(*rect)
            cr.set_source_rgba(1, 1, 1, 0.0)
            cr.set_operator(cairo.OPERATOR_SOURCE)                
            cr.paint()
        else:    
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)            
            cr.set_operator(cairo.OPERATOR_SOURCE)
            cr.set_source_rgb(0.9, 0.9, 0.9)
            cr.fill()
            
PopupWindow()            
