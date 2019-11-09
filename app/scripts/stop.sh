#!/bin/bash
kill $(ps aux | grep "python3 /home/pi/mycar/manage.py" | awk '{ print $2 }')
echo "stopped!"
