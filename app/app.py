#!/usr/bin/python

# Tornado app file

import tornado.ioloop
import tornado.web
import os.path

import config

from logparser import LogParser


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # process the log file
        statistics = LogParser()
        # modify returned into something usable:
        data = self.encap_data(statistics)
        # render page
        self.render("template.html", data=data)

    def encap_data(self, log):
        # manually get everything ready...
        status = log.find_currentstatus()
        if status == 'd.conn':
            status = "Connected"
        elif status == 'r.conn':
            status = "Connected"
        elif status == 'f.conn':
            status = "Disconnected"
        else:
            status = "Disconnected"

        status_datetime = log.find_currentstatus_datetime()

        # build the data data structure for the template...
        data = {
            'current_status' : status,
            'current_status_datetime' : status_datetime[0:-5],
            'num_fconn' : log.count_fconn,
            'num_rconn' : log.count_rconn,
            'num_dconn' : log.count_dconn,
            'total_downtime' : log.get_dhms_string(log.total_downtime),
            'avg_downtime' : log.find_avg_downtime(),
            'med_downtime' : log.calc_median_down(),
            'short_downtime' : log.find_shortest_downtime(),
            'long_downtime' : log.find_longest_downtime(),
            'total_uptime' : log.get_dhms_string(log.total_uptime),
            'med_uptime' : log.calc_median_up(),
            'avg_uptime' : log.find_avg_uptime(),
            'short_uptime' : log.find_shortest_uptime(),
            'long_uptime' : log.find_longest_uptime(),
            'latest_events' : log.find_latest_events(10),
            'records_since' : log.find_first_datetime()[0:-5],
            'records_time' : log.calc_totaltime() }

        # return the data structure.
        return data

    
# Set up the tornado application object
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler)
            #(r"/static/(.*)", tornado.web.StaticFileHandler, {'path': config.static_path}),
            # Add more paths here  tornado.web.StaticFileHandler, {'path': 'static/question1.html'}
        ]
        settings = {
            "template_path": config.TEMPLATE_PATH,
            "static_path": config.STATIC_PATH,
            "debug": True
        }
        tornado.web.Application.__init__(self, handlers, **settings)
        
if __name__ == "__main__":
    app = Application()
    app.listen(config.port)
    print "Starting tornado server on port %d" % (config.port)
    print config.base_dir, config.STATIC_PATH, config.TEMPLATE_PATH
    tornado.ioloop.IOLoop.instance().start()
