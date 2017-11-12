# sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
# sudo lsusf // lists usb devices 
# sudo cat /dev/ttyUSB0 // Reads serial data

from DBFunc import *
from UpdateMethods import *
from Utils import *
import gps
import os
import time
from datetime import datetime

os.system("sudo killall gpsd")
os.system("sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock")

session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
tableName = "tblGPSPoints"
gpsPoints = []
updateRan = False
timeSet = False
systemStart = time.time()
while True:
    try:
        report = None
        if type(session) is not type(None):
            report = session.next()
        if type(report) is not type(None) and report['class'] == 'TPV':
            data = extractReportData(report)
            speed = None
            if type(data) is not type(None): 
                gpsPoints.append(data)
                if timeSet == False:
                    os.system("sudo date -s " + data[2])
                    timeSet = True
                speed = data[4]
            if len(gpsPoints) >= 60 or (type(speed) is not type(None) and speed < 0.5 and len(gpsPoints) >= 10):
                try:
                    runInsertMany("INSERT OR IGNORE INTO " + tableName + " VALUES (?,?,?,?,?,?,?,?,?,?,?)", gpsPoints)
                except Exception as e:
                    addError("Error Adding GPS Points", "GPSLogger.py", "", str(e))
                gpsPoints = []
                if not updateRan:
                    addUpdate("StartUpLog", str(datetime.now()), systemStart, time.time())
                    updatedStays = False
                    try:
                        performStayPointUpdate()
                        updatedStays = True
                    except Exception as e:
                        addError("StayPointUpdateError" , "GPSLogger.py", "", str(e))
                    try:
                        if updatedStays:
                            performJourneyUpdate()
                    except Exception as e:
                        addError("JourneyUpdateError", "GPSLogger.py", "",  str(e))
                    updateRan = True
    except KeyboardInterrupt:
        quit()
    except StopIteration:
        session = None
        print("GPSD has terminated")
    except Exception as e:
        print(str(e))
        addError("GPSLogger Global Try Error", "GPSLogger.py", "",  str(e))
