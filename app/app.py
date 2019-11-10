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
from time import sleep


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
    stdout, stderr = MyOut.communicate(timeout=5)
    results = [stdout, stderr]
    return results

def terminal2(command):
    p = subprocess.Popen(command.split(" "))
    return p

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
         cmd,
         stdout=asyncio.subprocess.PIPE,
         stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()

    print("{0} exited with {1}".format(cmd, proc.returncode))
    if stdout:
        print('[stdout]\n{0}'.format(stdout.decode()))
    if stderr:
        print('[stderr]\n{0}'.format(stderr.decode()))


def no_errors(command):
    if command[1] == None:
        return True
    print('Error: ', command[1])
    #raise Exception("Error: ", command[1])


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #data = {'latest_events' : self.application.console }
        self.render("template.html")#, data=data)


    
# Set up the tornado application object
class LocalWebController(tornado.web.Application):
    def __init__(self):
        print("Starting Server...")

        this_dir = os.path.dirname(os.path.realpath(__file__))
        self.static_file_path = os.path.join(this_dir, 'templates', 'static')

        self.console = ["no messages"]
        self.model_list = []
        self.tasks = []

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
        #mount("/dev/sda1", "/home/pi/mycar/data")
        status = terminal("sudo mount /dev/sda1 /home/pi/mycar/data")


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
        terminal("cp /home/pi/mycar/data/*.h5 /home/pi/mycar/pilot/")
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
        terminal("sudo umount /home/pi/mycar/data")


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
        #donkey_dir = "/home/pi/mycar/pilot"
        #onlyfiles = [f for f in listdir(donkey_dir) if isfile(join(donkey_dir, f))]
        #print(onlyfiles)
	##data = {'tubs' : onlyfiles}
        #return self.render("templates/vehicle.html", **data)
        #terminal()


class TrainAPI(tornado.web.RequestHandler):

    #def get(self):
    #    data = {}
    #    self.render("templates/vehicle.html", **data)
    
    def post(self):
        '''
        Receive post requests as user changes the angle
        and throttle of the vehicle on a the index webpage
        '''
        data = tornado.escape.json_decode(self.request.body)
        print("data: ", data)
        #self.application.angle = data['angle']
        if data['command'] == 'rc':
            #status = terminal("python3 /home/pi/mycar/manage.py drive --js &")
            self.application.tasks.append(terminal2("python3 /home/pi/mycar/manage.py drive --js"))
        elif data['command'] == 'stop':
            for task in self.application.tasks:
                task.kill()
                del task


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
        #model_name = data['model']
        model_name = '/home/pi/mycar/pilot/pilot.h5'
        print("model name", model_name) 
        ## TODO: @hans Run a script that unmounts
        self.application.tasks.append(terminal2("python3 /home/pi/mycar/manage.py drive --model /home/pi/mycar/pilot/pilot.h5"))
        
if __name__ == "__main__":
    lwc = LocalWebController()
    lwc.update()
