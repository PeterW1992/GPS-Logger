# sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
# sudo lsusf // lists usb devices 
# sudo cat /dev/ttyUSB0 // Reads serial data

from DBFunc import *
import gps
import os
import time

os.system("sudo killall gpsd")
os.system("sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock")

session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
tableName = "tblGPSPoints"
gpsPoints = []
updateRan = False
systemStart = time.time()
while True:
    try:
        report = None
        if type(session) is not type(None):
            report = session.next()
        if type(report) is not type(None) and report['class'] == 'TPV':
            mode = None; lon = None; lat = None; dateTime = None; epx = None; epy = None; epv = None; ept = None; speed = None; alt = None; track = None
            if hasattr(report, 'mode'):
                mode = report.mode
            if hasattr(report, 'time'):
                if str(report.time)[0:4] != "1980":
                    dateTime = str(report.time)
            if type(mode) is not type(None) and mode == 3 and type(dateTime) is not type(None):
                if hasattr(report, 'lon'): 
                    lon = report.lon				
                if hasattr(report, 'lat'): 
                    lat = report.lat
                if hasattr(report, 'time'):
                    dateTime = str(report.time)
                if hasattr(report, 'epx'): 
                    epx = report.epx
                if hasattr(report, 'epy'): 
                    epy = report.epy
                if hasattr(report, 'epv'): 
                    epv = report.epv
                if hasattr(report, 'ept'):
                    ept = report.ept
                if hasattr(report, 'speed'): 
                    speed = report.speed			
                if hasattr(report, 'alt'):
                    alt = report.alt
                if hasattr(report, 'track'):
                    track = report.track
                asTuple = (lat, lon, dateTime, alt, speed, epx, epy, epv, ept, mode, track)
                gpsPoints.append(asTuple)
            if len(gpsPoints) >= 60 or (type(speed) is not type(None) and speed < 0.5 and len(gpsPoints) >= 10):
                try:
                    runInsertMany("INSERT OR IGNORE INTO " + tableName + " VALUES (?,?,?,?,?,?,?,?,?,?,?)", gpsPoints)
                except Exception as e:
                    addError("Error Adding GPS Points", "GPSLogger.py", "", str(e))
                gpsPoints = []
                if not updateRan:
                    addUpdate("StartUpLog", "", systemStart, time.time())
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
        addError("GPSLogger Global Try Error", "GPSLogger.py", "",  str(e))
