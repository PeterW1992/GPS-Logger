from Utils import *
import sqlite3
import time as timer

dbFields = ["Lat", "Lon", "DateTime", "Alt", "Speed", "Epx", "Epy", "Epz", "Ept", "Mode", "Track"]

class StayPoint(object):
    lat = 0.0
    lon = 0.0
    start = ""
    end = ""
    row_id = -1
    
    def __init__(self, lat, lon, start, end):
        self.lat = lat
        self.lon = lon
        self.start = start
        self.end = end

    def __hash__(self):
        return hash((self.lat, self.lon))

    def __eq__(self, other):
        return (self.lat, self.lon) == (other.lat, other.lon)
	
    def __ne__(self, other):
       	return not(self == other)

class Journey(object):
    startStayPoint = -1
    endStayPoint = -1
    start = ""
    end = ""

    def __init__(self, startStay, endStay, start, end):
        self.startStayPoint = startStay
        self.endStayPoint = endStay
        self.start = start
        self.end = end

def getSummary():
    fileSize = (str(getDBFileSize()), )
    pointCount = (str(getRecordCountFor("tblGPSPoints")), )
    stayCount = (str(getRecordCountFor("tblStayPoints")), )
    visitCount = (str(getRecordCountFor("tblStayPointVisits")), )
    journeyCount = (str(getRecordCountFor("tblJourneys")), )
    latestPoint = (getLatestDateTime(), )
    oldestPoint = (getOldestDateTime(), )
    latestStayUpdate = (getLatestUpdateTime("StayPointUpdate"), )
    latestJourneyUpdate  = (getLatestUpdateTime("JourneyUpdate"), )
    output = []
    output.append(fileSize)
    output.append(pointCount)
    output.append(stayCount)
    output.append(visitCount)
    output.append(journeyCount)
    output.append(latestPoint)
    output.append(oldestPoint)
    output.append(latestStayUpdate)
    output.append(latestJourneyUpdate)
    return output

def printModeCount():
    allPoints = runQuery("SELECT Mode, COUNT(Mode) FROM tblGPSPoints GROUP BY Mode")
    for record in allPoints:
        print("Mode: " + str(record[0]) + ", Count: " + str(record[1]))

def printLatestMode1():
    allPoints = runQuery("SELECT MAX(dateTime), * FROM tblGPSPoints WHERE MODE = 1")
    print(allPoints)

def getLatestVisit():
    record = runQuery("SELECT MAX(endTime),* FROM tblStayPointVisits")[0]
    return record

def getLatestVisitStr():
    record = getLatestVisit()
    returnStr = "No Visits"
    if record[0] != None:
        returnStr = "Latest Visit: %d - Start: %s, End: %s" % (record[1], record[2], record[3])
    return returnStr

def getLatestJourneyStr(): 
    record = runQuery("SELECT MAX(endTime),* FROM tblJourneys")[0]
    returnStr = "No Journeys"	
    if record[0] != None:
        returnStr = "Latest Journey: %d to %d - Start: %s, End: %s" % (record[1], record[2], record[3], record[4])
    return returnStr

def getPointsAfter(date):
    points = runQuery("SELECT Lat,Lon,dateTime FROM tblGPSPoints WHERE date(dateTime) > strftime('%Y-%m-%d',\'" + date + "\') AND Lat IS NOT NULL AND Lon IS NOT NULL")
    return points 

def getStayPoints():
    points = runQuery("SELECT rowid, * FROM tblStayPoints")
    return points

def getOldestDateTime():
    query = "SELECT MIN(dateTime) FROM tblGPSPoints"
    oldest = runQuery(query)[0][0]
    return oldest

def getRecordCountFor(tableName):
    query = "SELECT COUNT(*) FROM %s" % (tableName)
    count = runQuery(query)[0][0]
    return count

def getLatestUpdateTime(type):
    query = "SELECT MAX(dateTime) FROM tblUpdates WHERE type = '%s'" % (type)
    lastUpdate = runQuery(query)[0][0]
    return lastUpdate

def addUpdate(updateType, dateTime, startTime, endTime):
    update = "INSERT INTO tblUpdates VALUES ('%s', '%s', %f, %f)" % (updateType, dateTime, startTime, endTime)
    runInsert(update)

def getLatestDateTime():
    getLatest = "SELECT MAX(dateTime) FROM tblGPSPoints"
    latest = runQuery(getLatest)[0][0]
    return latest
   
def getJourneyPoints(journeys):
    ids = []
    for journey in journeys:
        ids.append(journey[0])
    idStr = str(ids)[1:-1]
    query = "SELECT tblGPSPoints.rowid, Lat, Lon, dateTime, Alt, Speed, Mode, Track, tblJourneyPoints.JourneyID FROM tblJourneyPoints INNER JOIN tblGPSPoints ON tblJourneyPoints.pointID = tblGPSPoints.rowid WHERE tblJourneyPoints.JourneyID IN (" + idStr + ")"
    points = runQuery(query)
    return points

def getJourneysAfter(dateTime):
    if len(dateTime) > 0:
        query = "SELECT rowid, * FROM tblJourneys WHERE strftime('%Y-%m-%dT%H:%M:%S', startTime) >  strftime('%Y-%m-%dT%H:%M:%S',\'" + dateTime + "\')"
    else:
        query = "SELECT rowid, * FROM tblJourneys"
    points = runQuery(query)
    return points

def getVisitsAfter(dateTime):
    dateTime = ""
    if dateTime == "":
        query = "SELECT * FROM tblStayPointVisits ORDER BY startTime"
    else:
        query = "SELECT * FROM tblStayPointVisits WHERE end > %s ORDER BY startTime" % (str(dateTime))
    records = runQuery(query)
    return records

def runInsertMany(insert, data):
    conn = sqlite3.connect("GPSLogger.db", timeout=2000)
    cur = conn.cursor()
    cur.executemany(insert, data)
    conn.commit()
    cur.close()
    conn.close()

def runInsert(insert):
    conn = sqlite3.connect("GPSLogger.db", timeout=2000)
    cur = conn.cursor()
    insertNo = cur.execute(insert)
    conn.commit()
    cur.close()
    conn.close()
    return insertNo

def runDelete(delete):
    conn = sqlite3.connect("GPSLogger.db", timeout=2000)
    cur = conn.cursor()
    cur.execute(delete)
    conn.commit()
    cur.close()
    conn.close()

def runQuery(query):
    conn = sqlite3.connect("GPSLogger.db", timeout=2000)
    cur = conn.cursor()
    cur.execute(query)
    records = cur.fetchall()
    cur.close()
    conn.close()
    return records

def addError(errorType, fileName, gpsTime, errorDesc):
    runInsert("INSERT INTO tblErrors VALUES (%s, %s, %f, %s, %s)") %(errorType, fileName, timer.time(), gpsTime, errorDesc)
