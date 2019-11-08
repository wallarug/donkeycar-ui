#!/bin/usr/python

#
# Internet Uptime Log Parser
#

import datetime
import time
import shlex

class LogParser:
   def __init__(self):
      self.total_downtime = 0
      self.total_uptime = 0
      self.count_rconn = 1
      self.count_dconn = 1
      self.count_fconn = 1
      self.total_records = 0

      self.next = 0

      self.stats = {}

      self.parse()

   def parse(self):
      # open the file
      f = open("network-activity-log.txt", "r")

      # read all the contents
      contents = f.readlines()

      stats = []

      # go through and tally up some statistics
      
      for line in contents:
         # create a statistics object
         item = Stat(line)

         # filter out all the dns spam
         if "dns" in item.message:
            pass
         else:
            self.total_records += 1
            #print self.total_records
            self.tally(item)
            stats.append(item)

      self.stats = stats

   def tally(self, item):
      if item.type == 'r.conn':
         self.total_downtime += item.duration
         self.count_rconn += 1
      elif item.type == 'f.conn':
         self.total_uptime += item.duration
         self.count_fconn += 1
      elif item.type == 'd.conn':
         self.count_dconn += 1

   ## OUTPUT METHODS
   def summary(self):
      print " *** LOGGER SUMMARY"
      print " * Lost Connection: {0}".format(str(self.count_dconn))
      print " * Failed Connection: {0}".format(str(self.count_fconn))
      print " * Reconnected: {0}".format(str(self.count_rconn))
      x = self.total_downtime
      time = self.get_dhms_string(x)
      percentage = self.get_percentage(x)
      print " * Total Down time: {0} ({1}%)".format(time, str(percentage))

      x = self.total_uptime
      time = self.get_dhms_string(x)
      percentage = self.get_percentage(x)      
      print " * Total Up time: {0} ({1}%)".format(time, str(percentage))

      x = (self.total_downtime / self.count_dconn)
      time = self.get_hms_string(x)
      print " * Average Down time: {0}".format(time)

      x = (self.total_uptime / self.count_rconn)
      time = self.get_hms_string(x)
      print " * Average Up time: {0}".format(time)
      print " *** END OF SUMMARY "

   def display(self):
      for item in self.stats:
         print item

   ## POINTER NAVIGATION
   def get_last(self):
      print self.stats[-1]

   def get_first(self):
      print self.stats[0]

   def get_next(self):
      self.next += 1
      print self.stats[self.next]

   def get_prev(self):
      self.next = self.next - 1
      print self.stats[self.next]

   def get_curr(self):
      print self.stats[self.next]

   ## HELPER FUNCTIONS
   def get_hms_string(self, x):
      hours, minutes, seconds = 0, 0, 0
      if x != 0:
         minutes, seconds = divmod(x, 60)
      if minutes != 0:
         hours, minutes = divmod(minutes, 60)
      rtn = "{0}h {1}m {2}s".format(str(int(hours)),
                                           str(int(minutes)),
                                           str(int(seconds)))
      return rtn

   def get_dhms_string(self, x):
      days, hours, minutes, seconds = 0, 0, 0, 0
      if x != 0:
         minutes, seconds = divmod(x, 60)
      if minutes != 0:
         hours, minutes = divmod(minutes, 60)
      if hours != 0:
         days, hours = divmod(hours, 24)

      rtn = "{3}d {0}h {1}m {2}s".format(str(int(hours)),
                                           str(int(minutes)),
                                           str(int(seconds)),
                                           str(int(days)))
      return rtn

   def get_percentage(self, x):
      return round(x / (self.total_uptime + self.total_downtime), 2) * 100


   ## SEARCH METHODS
   def find_shortest_downtime(self):
      short = 99999
      i_short = None
      for item in self.stats:
         if item.type == 'r.conn' and item.duration < short and item.duration > 2:
            short = item.duration
            i_short = item
      return self.get_hms_string(short)

   def find_shortest_uptime(self):
      short = 99999
      i_short = None
      for item in self.stats:
         if item.type == 'f.conn' and item.duration < short and item.duration > 2:
            short = item.duration
            i_short = item
      return self.get_hms_string(short)

   def find_longest_downtime(self):
      short = 0
      i_short = None
      for item in self.stats:
         if item.type == 'r.conn' and item.duration > short:
            short = item.duration
            i_short = item
      return self.get_hms_string(short)

   def find_longest_uptime(self):
      short = 0
      i_short = None
      for item in self.stats:
         if item.type == 'f.conn' and item.duration > short:
            short = item.duration
            i_short = item
      return self.get_hms_string(short)

   def find_currentstatus(self):
      return self.stats[-1].type

   def find_currentstatus_datetime(self):
      return self.stats[-1].date + " " + self.stats[-1].time

   def find_first_datetime(self):
      return self.stats[0].date + " " + self.stats[0].time

   def find_avg_downtime(self):
      return self.get_hms_string((self.total_downtime / self.count_dconn))

   def find_avg_uptime(self):
      return self.get_hms_string((self.total_uptime / self.count_rconn))

   def find_latest_events(self, limit):
      events = []
      i = 1
      while i < limit + 1:
         events.append(self.stats[-i].message)
         i += 1
      return events

   ## Calculations
   def calc_median_down(self):
      values = []
      for item in self.stats:
         if item.type == 'r.conn':
            values.append(item.duration)
      values.sort()
      if len(values) < 2:
         return "NA"
      return self.get_hms_string(values[len(values)/2])

   def calc_median_up(self):
      values = []
      for item in self.stats:
         if item.type == 'f.conn':
            values.append(item.duration)
      values.sort()
      if len(values) < 2:
         return "NA"
      return self.get_hms_string(values[len(values)/2])

   def calc_totaltime(self):
      return self.get_dhms_string(self.total_uptime + self.total_downtime)




class Stat:
      def __init__(self, message):
         # type:
         #  reconnected [RECONNECTED]
         #  connected [CONNECTED]
         #  disconnection [CONNECTION **LOST**]
         #  failure [STATUS **FAIL**]
         self.type = ""
         self.duration = 0
         self.date = ""
         self.time = ""
         self.message = ""

         self.parse(message)

      def __str__(self):
         return self.message

      def __name__(self):
         return self.message

      def parse(self, message):
         parts = message.split(" ")
         self.date = parts[0]
         self.time = parts[1]

         self.type = self.check_status(parts[2])

         if self.type == 'r.conn' or self.type == 'f.conn':
            if float(parts[-1]) < 1:
               self.type = self.type + "-invalid"
            self.duration = float(parts[-1])
         else:
            self.duration = -1

         self.message = message

      def check_status(self, s):
         if s == '[RECONNECTED]':
            return "r.conn"
         elif s == '[CONNECTED]':
            return "d.conn"
         elif s == '[CONNECTION':
            return "f.conn"
         elif s == '[STATUS **FAIL**]':
            return "f.dev"
         elif s == '[STATUS OK]':
            return "info"
         else:
            return "unknown"
         
