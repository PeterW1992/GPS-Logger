from DBFunc import *
import gps
import os
import time

session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
tableName = "tblGPSPoints"
gpsPoints = []
updateRan = False
systemStart = time.time()
while True:
    try:
        mode = None; lon = None; lat = None; dateTime = None; epx = None; epy = None; epv = None; ept = None; speed = None; alt = None; track = None
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
