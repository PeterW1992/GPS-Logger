#!/bin/sh
# startUp.sh
# navigate to home directory, then to this directory, then execute python scripts then back home
sleep 5
cd /
cd home/pi/GPS-Logger/Code
sudo hciconfig hci0 piscan
sudo python GPSLogger.py &
sudo python BlueServer.py &
cd /
