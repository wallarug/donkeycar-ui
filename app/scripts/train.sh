#!/bin/bash

#$a = exec('/home/pi/mycar/manage.py drive --js > /dev/null 2>&1 echo $!');
/home/pi/mycar/manage.py drive --js;
echo "started!";
