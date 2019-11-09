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

from os.path import join, isdir, exists
from os import path, listdir
import sys
import subprocess
from shutil import copyfile

import config

# for python3.8.0 windows
# python-3.8.0a4
import asyncio
#asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



def terminal(command):
    MyOut = subprocess.Popen(
      command.split(" "),
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT
    )
    stdout, stderr = MyOut.communicate(timeout=60)
    results = [stdout, stderr]
    return results

def mount(device, mountpoint):
    finished = False
    loops = 5
    while(not finished and loops > 0):
        sleep(1)
        results = terminal("mount {0} {1}".format(device, mountpoint))
        no_errors(results)
        log_file.line(results[0])
        if(
            "mount:" not in str(results[0])
        ):
            finished = True
        loops-=1

    if(not finished):
        error("Error mounting {0}".format(mountpoint))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        data = {'latest_events' : self.application.console }
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
            (r"/mount", MountAPI),
            (r"/copy", CopyAPI),
            (r"/unmount",UnmountAPI),
            (r"/tub",TubAPI),
            (r"/train",TrainAPI),
            (r"/model",ModelAPI),
            
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": self.static_file_path}),
            #(r"/static/(.*)", tornado.web.StaticFileHandler, {'path': config.static_path}),
            # Add more paths here  tornado.web.StaticFileHandler, {'path': 'static/question1.html'}
        ]

        #settings = {'debug': True}

        settings = {
            "template_path": config.TEMPLATE_PATH,
            "static_path": config.STATIC_PATH,
            "debug": True
        }
        #tornado.web.Application.__init__(self, handlers, **settings)
        super().__init__(handlers, **settings)

    def update(self, port=8888):
        ''' Start the tornado webserver. '''
        asyncio.set_event_loop(asyncio.new_event_loop())
        print(port)
        self.port = int(port)
        self.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()



class MountAPI(tornado.web.RequestHandler):

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
        print("Mounting USB")
        ## TODO: @hans Run a script that mounts and copies
        mount("/dev/sda", "/media/usb/")


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
        print("Copying Data to USB")
        ## TODO: @hans Run a script that mounts and copies
        terminal()
        #copyfile("../board-undertest/code.py", "/media/circuitpython/code.py")


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
        print("Unmounting USB")
        ## TODO: @hans Run a script that unmounts
        terminal()


class TubAPI(tornado.web.RequestHandler):

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
        print("latest Tub Name")
        ## TODO: @hans Run a script that unmounts
        terminal()


class TrainAPI(tornado.web.RequestHandler):

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
        print("Start Training")
        ## TODO: @hans Run a script that unmounts
        terminal()


class ModelAPI(tornado.web.RequestHandler):

    #def get(self):
    #    data = {}
    #    self.render("templates/vehicle.html", **data)
    
    def post(self):
        '''
        Receive post requests as user changes the angle
        and throttle of the vehicle on a the index webpage
        '''
        data = tornado.escape.json_decode(self.request.body)
        #self.application.angle = data['angle']
        print("Start Model")
        model_name = data['model']
        print("model name", model_name) 
        ## TODO: @hans Run a script that unmounts
        terminal()
        
if __name__ == "__main__":
    lwc = LocalWebController()
    lwc.update()
