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


## Helper Function for dealing with running shell scripts
currentProcess = None
def terminal(cmd):
    args = cmd.split(" ")
    global currentProcess
    currentProcess = Popen(args, stdout=PIPE, bufsize=0)
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
        print("TimeoutException: the process took too long to response.")
        print(e.stdout)
        return "error: TimeoutException"

def readconsole():
    global currentProcess
    count = 0
    output = ""
    try:
        if currentProcess is not None and currentProcess.poll() == None:
            output = ""
            print("loop start")
            print(currentProcess.stdout)
            for line in currentProcess.stdout.readlines():
                print(line)
                if line == '' and count < 1:
                    break
                if line:
                    output = output + line.strip() + '\n'
                count += 1
        return output
    except Exception as e:
        print("something went wrong. ", e)
        return "Unknown Error"

def readconsoleline():
    global currentProcess
    try:
        if currentProcess is not None and currentProcess.poll() == None:
           print(currentProcess.args)
           print(currentProcess.stdout)
           print(currentProcess.stderr)
           print(currentProcess.pid)
           print(currentProcess)
           while True:
               line = currentProcess.stdout.readline()
               if not line:
                   break
               print(line)
           #for ln in currentProcess.stdout.readline():
           #    print(ln)
           #print(currentProcess.stdout)
           #out = currentProcess.stdout.read()
           #print(out)
           #return out.decode('utf-8')
    except Exception as e:
        print("exception: ", e)
        return "Unknown Error"

def stop():
    try:
        if currentProcess is not None:
            pid = currentProcess.pid
            currentProcess.terminate()
            code = currentProcess.returncode
            out, err = currentProcess.communicate()
            text = "terminated process with pid {0} and return code {1}\n{2}".format(pid, code, out)
            print(text)
            return text
        else:
            return "No process running!"
    except TimeoutExpired:
        print("TimeoutException: the process took too long to response.")
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
            terminal("sudo mount /dev/sda1 /home/pi/mycar/data")
            text = console()
        elif cmd == 'usb/unmount':
            # unmount the USB drive
            terminal("sudo umount /home/pi/mycar/data")
            text = console()

        ## Tub and File operations
        elif cmd == 'tub/details':
            # get the latest information about the tubs on the server
            pass

        ## Training Operations
        elif cmd == 'train/start':
            #terminal("python /home/pi/newcar/manage.py drive --js")
            #terminal("python /home/pi/newcar/manage.py drive")
            terminal("python test.py")
            text = "started!" #console()

        elif cmd == 'train/stop':
            text = stop()

        elif cmd == 'train/status':
            text = readconsoleline()

        ## AI Operations
        elif cmd == 'ai/start':
            pass

        elif cmd == 'ai/stop':
            pass

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

    
# Set up the tornado application object
##class LocalWebController(tornado.web.Application):
##    def __init__(self):
##        print("Starting Server...")
##
##        handlers = [
##            #(r"/", tornado.web.RedirectHandler, dict(url="/drive")),
##            (r"/", MainHandler),
##            (r"/mount", MountAPI),
##            (r"/copy", CopyAPI),
##            (r"/unmount",UnmountAPI),
##            (r"/tub",TubAPI),
##            (r"/train",TrainAPI),
##            (r"/model",ModelAPI),
##            
##            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": self.static_file_path}),
##            #(r"/static/(.*)", tornado.web.StaticFileHandler, {'path': config.static_path}),
##            # Add more paths here  tornado.web.StaticFileHandler, {'path': 'static/question1.html'}
##        ]



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


## Run this when the file is opened.
if __name__ == "__main__":
    app = WebApp()
    app.start(PORT)

