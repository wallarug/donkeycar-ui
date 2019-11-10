#!/bin/bash

#$a = exec('/home/pi/mycar/manage.py drive --js > /dev/null 2>&1 echo $!');
python3 /home/pi/mycar/manage.py drive --js &>donkey.txt &
echo "started!"
