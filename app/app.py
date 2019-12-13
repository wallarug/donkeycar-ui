#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 08 12:10:44 2019

@author: wallarug

remotes.py

The server to run remote commands needed to manage a car remotely. 
"""
import tornado.ioloop
import tornado.web
import asyncio

from os.path import join, realpath, dirname
import json

from subprocess import Popen, PIPE, STDOUT, TimeoutExpired, check_output
import sys

# for python3.8.0 windows
# python-3.8.0a4
import asyncio
#asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

## Variables for Application
#import config
PORT = 8888
DEBUG = True

## Paths
APP_PATH = dirname(realpath(__file__))
TEMPLATE_PATH = join(APP_PATH, 'templates')
STATIC_PATH = join(APP_PATH, 'static')
DONKEY_PATH = '/home/pi/newcar/'
DONKEY_MODEL = 'pilot.h5'
USB_DEVICE = '/dev/sda1'

#FILE = open('output.txt', 'r+')


## Helper Function for dealing with running shell scripts
currentProcess = None
def terminal(cmd):
    args = cmd.split(" ")
    global currentProcess
    currentProcess = Popen(args, stdout=PIPE, stderr=STDOUT)
    #stdout, stderr = currentProcess.communicate(timeout=1)
    #print(stdout)
    #print(stderr)

def console():
    try:
        if currentProcess is not None and currentProcess.poll() == None:
            out, err = currentProcess.communicate(timeout=1)
            print("stdout:", out)
            return out.decode("utf-8")
        else:
            return "No process running!"

    except TimeoutExpired as e:
        print("TimeoutException: the process took too long to respond.")
        if currentProcess.poll() == None:
            return "still running with PID {0} but unable to read stdout. error: TimeoutException.".format(currentProcess.pid)

def stop():
    try:
        if currentProcess is not None:
            pid = currentProcess.pid
            currentProcess.terminate()
            code = currentProcess.returncode
            text = "terminated process with pid {0} and return code {1}\n".format(pid, code)
            print(text)
            return text
        else:
            return "No process running!"
    except TimeoutExpired:
        print("TimeoutException: the process took too long to respond.")
        return "error: TimeoutException"



## WebController Application Class
##   This is used to make changing settings easier and high-levels of customising the settings
##    that make the application run.
class WebApp(tornado.web.Application):
    def __init__(self):
        ## Set up all the application customised settings here for the webserver.  This is
        ##  easier than having seperate variables to pass in.

        ## Settings
        settings = {
            "template_path": TEMPLATE_PATH,
            "static_path": STATIC_PATH,
            "static_url_prefix" : "/static/",
            "debug": True,
            "autoreload" : True
        }

        ## Handlers
        handlers = [
            (r"/", MainHandler),
        ]

        ## Initialise the Application
        super().__init__(handlers, **settings)

    def start(self, port=8888):
        ''' Start the tornado webserver. '''
        asyncio.set_event_loop(asyncio.new_event_loop())
        print(port)
        self.port = int(port)
        self.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()


## Handler
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        models = ["Item 1", "Item 2", "Item 3"]
        self.render("example.html", title="Sample", models=models)

    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        print("data: ", data['command'])

        result = "unknown command. no action"

        cmd = data['command']

        ## USB Operations
        if cmd == 'usb/mount':
            # mount the USB drive
            path = join(DONKEY_PATH, 'data')
            command = "sudo mount " + USB_DEVICE + " " + path
            terminal(command)
            #terminal("sudo mount /dev/sda1 /home/pi/mycar/data")
            text = console()
        elif cmd == 'usb/unmount':
            # unmount the USB drive
            terminal("sudo umount " + DONKEY_PATH + "data")
            text = console()

        ## Tub and File operations
        elif cmd == 'tub/details':
            # get the latest information about the tubs on the server
            # tub folder
            path = join(DONKEY_PATH, 'data')
            cmd = Popen(["ls", path, "-1t"], stdout=PIPE, stderr=STDOUT)
            folder = check_output(["head", "-1"], stdin=cmd.stdout, text=True)
            # latest file
            path = join(path, folder.strip())
            cmd = Popen(["ls", path, "-1t"], stdout=PIPE, stderr=STDOUT)
            latest = check_output(["head", "-1"], stdin=cmd.stdout, text=True)
            # file count
            cmd = Popen(["ls", path, "-l"], stdout=PIPE, stderr=STDOUT)
            lines = check_output(["wc", "-l"], stdin=cmd.stdout, text=True)
            lines = int((int(lines) / 2) - 2)
            # return
            print(folder, latest, lines)
            text = "Tub Name: {0}\nLatest File: {1}\nNumber of Images: {2}".format(folder, latest, lines)

        ## Training Operations
        elif cmd == 'train/start':
            terminal("python " + DONKEY_PATH + "manage.py drive --js")
            text = "started!" #console()

        elif cmd == 'train/stop':
            text = stop()

        elif cmd == 'train/status':
            text = console()

        ## AI Operations
        elif cmd == 'ai/start':
            terminal("python " + DONKEY_PATH + "manage.py drive --model=" + DONKEY_PATH + "/pilot/" + DONKEY_MODEL)
            text = "started! Model: " + DONKEY_MODEL

        elif cmd == 'ai/stop':
            text = stop()

        elif cmd == 'ai/status':
            text = console()

        elif cmd == 'ai/list':
            pass

        elif cmd == 'ai/custom':
            pass

        if data['command'] == 'console':
            text = 'hello world'
        
        self.set_header("Content-Type", "application/json")
        self.write({'text': text})


## Run this when the file is opened.
if __name__ == "__main__":
    app = WebApp()
    app.start(PORT)
