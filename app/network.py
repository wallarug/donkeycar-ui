#!/bin/usr/python

#
# Internet Uptime Logger
#
# This script sends out packets to check if the internet
# connection is online.  If the connection is not online,
# it will log it into a file, detailing the date, time and
# duration of the down time.
#
# Extension: Run a speed test every 15 minutes and log the
#  speed (download and upload)
#

import os
import socket
import subprocess
import datetime
import shlex
import time


class ConnectionLogger:
   """
   Class that handles all network and logging.
   """
   def __init__(self):
      self.statuschecker()
      # Determine OS running suite (different settings for Windows
      #  vs Linux/GNU.
      
      

   def internet(self, host="8.8.8.8", port=53, timeout=3):
      #
      # Attempts to connect to a given DNS server.
      #
      """
      ~~Default~~
      Host: 8.8.8.8 (google-public-dns-a.google.com)
      OpenPort: 53/tcp
      Service: domain (DNS/TCP)
      """
      try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
      except Exception as ex:
        #logger(ex.message)
        return False

   def ping(self, hostname='8.8.8.8'):
      #
      # Executes a ping request to given server.
      #
      #cmd = 'ping {0} -n 1'
      cmd = 'ping -c 1 {0}'
      return not os.system(cmd.format(hostname))

   def get_time(self):
      #
      # Returns current system time in custom format
      #
      #dt = datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%SGMT+0')
      #return dt
      return str(datetime.datetime.now())

   def logger(self, message):
      # open file
      f = open("network-activity-log.txt", "a")
      # add line to log file
      f.write("\n")
      f.write(message)
      # close file
      f.close()

   def statuschecker(self):
      """ Determines what is actually broken and the length of down time. """
      # set up some variables
      uptime = 0
      downtime = 0
      disconnects = 0
      isConnected = True
      hasIssue = False

      self.logger("{0} [INFO]  monitoring network up and down times.".format(self.get_time()))

      while True:
        # this loop will run forever until I stop the program
        uptime = time.time()

        # provide basic message confirming we are connected to the internet:
        self.logger("{0} [CONNECTED]  Internet is connected. Monitoring...".format(self.get_time()))

        # the good loop:
        while isConnected and hasIssue == False:
            # check that the conection is still good by
            #  connecting to the google DNS
            if self.internet("8.8.8.8"):
                time.sleep(1.0)
            else:
                # something has broken, let's check it's not Google DNS first.
                hasIssue = True
                if self.internet("8.8.4.4"):
                    # we can still connect to things outside
                    hasIssue = False
                else:
                    # assume internet disconnected... go to diagostics:
                    isConnected = False

        # diagonse issue first (is it internal?)
        uptime = time.time() - uptime
        self.logger("{0} [CONNECTION **LOST**]  cannot connect to the internet.  Uptime: {1}".format(self.get_time(), uptime)) 
##        if not internet("192.168.12.254"):
##            logger("{0} [STATUS **FAIL**]  cannot connect to FritzBox (192.168.12.254)".format(get_time()))
##        else:
##            logger("{0} [STATUS OK]  FritzBox (192.168.12.254) is online.".format(get_time()))
##
##        if not internet("192.168.1.1"):
##            logger("{0} [STATUS **FAIL**]  cannot connect to HUAWEI HG659 (192.168.1.1)".format(get_time()))
##        else:
##            logger("{0} [STATUS OK]  HUAWEI HG659 (192.168.1.1) is online.".format(get_time()))


        self.logger("{0} [ATTEMPTING RECONNECT]  waiting for connection...".format(self.get_time()))
        
        downtime = time.time()
        # the bad loop
        while hasIssue:
            # keep checking until the internet comes back online:
            if self.internet("8.8.8.8") and self.ping("8.8.8.8"):
               # full internet services have been restored.
               hasIssue = False
               isConnected = True
               downtime = time.time() - downtime
               self.logger("{0} [RECONNECTED]  successfully reconnected to internet.  Downtime: {1}".format(self.get_time(), downtime))
            elif self.internet("8.8.8.8") and not self.ping("8.8.8.8"):
               # partial internet services have been restored.
               self.logger("{0} [STATUS OK]  dns services have been restored but not internet (ping).  Downtime: {1}".format(self.get_time(), ( time.time() - downtime )))
               time.sleep(5.0)
            else:
               # no internet services have been restored.
               time.sleep(1.0)


         

      

if __name__ == '__main__':
    try:
        ConnectionLogger()
    except KeyboardInterrupt:
        exit(0)


    
    
