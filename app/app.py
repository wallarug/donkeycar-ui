#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 08 12:10:44 2019

@author: wallarug

remotes.py

The server to run remote commands needed to manage a car remotely. 
"""

import os
import json
import time
import asyncio

import requests
import tornado.ioloop
import tornado.web
import tornado.gen

import config


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("template.html", data=data)


    
# Set up the tornado application object
class LocalWebController(tornado.web.Application):
    def __init__(self):
        print("Starting Server...")

        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.static_file_path = os.path.join(this_dir, 'templates', 'static')

        self.console = "no messages"
        
        handlers = [
            #(r"/", tornado.web.RedirectHandler, dict(url="/drive")),
            (r"/", MainHandler),
            (r"/copy", CopyAPI),
            (r"/unmount",UnmountAPI),
            
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": self.static_file_path}),
            #(r"/static/(.*)", tornado.web.StaticFileHandler, {'path': config.static_path}),
            # Add more paths here  tornado.web.StaticFileHandler, {'path': 'static/question1.html'}
        ]

        settings = {'debug': True}

        #settings = {
        #    "template_path": config.TEMPLATE_PATH,
        #    "static_path": config.STATIC_PATH,
        #    "debug": True
        #}
        #tornado.web.Application.__init__(self, handlers, **settings)
        super().__init__(handlers, **settings)


class CopyAPI(tornado.web.RequestHandler):

    #def get(self):
    #    data = {}
    #    self.render("templates/vehicle.html", **data)
    
    def post(self):
        '''
        Receive post requests as user changes the angle
        and throttle of the vehicle on a the index webpage
        '''
        #data = tornado.escape.json_decode(self.request.body)
        #self.application.angle = data['angle']
        
        ## TODO: @hans Run a script that mounts and copies


class UnmountAPI(tornado.web.RequestHandler):

    #def get(self):
    #    data = {}
    #    self.render("templates/vehicle.html", **data)
    
    def post(self):
        '''
        Receive post requests as user changes the angle
        and throttle of the vehicle on a the index webpage
        '''
        #data = tornado.escape.json_decode(self.request.body)
        #self.application.angle = data['angle']
        
        ## TODO: @hans Run a script that unmounts
        
if __name__ == "__main__":
    app = Application()
    app.listen(config.port)
    print "Starting tornado server on port %d" % (config.port)
    print config.base_dir, config.STATIC_PATH, config.TEMPLATE_PATH
    tornado.ioloop.IOLoop.instance().start()
