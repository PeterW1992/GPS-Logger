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

def getSettings():
    settings = open("Settings.txt", 'r')
    splSetting = settings.read().split("||")
    settings.close()
    output = {}
    for setting in splSetting:
        settingName = setting.split("=")[0]
        settingValue = float(setting.split("=")[1])
        output[settingName] = settingValue
    return output

settings = getSettings()
stayLength = settings["stayLength"]
stayRadius = settings["stayRadius"]
dist = settings["distVal"]

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

def stayPointsAfter(date):
    global stayRadius;global stayLength
    if len(date) == 0:
        query = "SELECT *, rowid FROM tblGPSPoints WHERE LAT IS NOT NULL AND dateTime is not NULL GROUP BY strftime('%Y-%m-%dT%H:%M', dateTime) ORDER BY dateTime ASC"
    else:
        query = "SELECT *, rowid FROM tblGPSPoints WHERE LAT IS NOT NULL AND strftime('%Y-%m-%dT%H:%M:%S', dateTime) >= strftime('%Y-%m-%dT%H:%M:%S',\'" + date + "\') GROUP BY strftime('%Y-%m-%dT%H:%M', dateTime) ORDER BY dateTime ASC"
    points = runQuery(query)
    stayPoints = []
    pointCount = len(points)
    prevPoint = None
    i = 0
    while i < pointCount:
        date = getDateTime(points[i][2])
        if type(prevPoint) is not type(None):
            prevDate = getDateTime(prevPoint[2])
            minutesDiff = (date - prevDate).total_seconds() / 60
            if minutesDiff >= stayLength:
                startMinute = prevDate.replace(microsecond=0).isoformat()
                endMinute = date.replace(microsecond=0).isoformat()
                startPoint = getPointInMinute("MAX", startMinute)
                endPoint = getPointInMinute("MIN", endMinute)
                start = startPoint[2]
                end = endPoint[2]
                if type(startPoint[0]) is not type(None) and type(endPoint[0]) is not type(None):
                    lat1 = startPoint[0];lon1 = startPoint[1];
                    #lat2 = endPoint[0];lon2 = endPoint[1]
                    #distance = getDistance(lat1, lon1, lat2, lon2)
                    # found end/start of end of stay point, need to find start of journey
                    #if distance <= stayRadius:
                    #    stayPoints.append(StayPoint(lat1, lon1, start, end))
                    #else:
                    #    print("Distance to great: %s" % str(distance,))
                    stayPoints.append(StayPoint(lat1, lon1, start, end))
                else:
                    print("Start or end visit date time was null")
        prevPoint = points[i]
        i += 1
    return stayPoints

def getPointInMinute(func, date):
    query = "SELECT Lat, Lon," + func + "(DateTime) FROM tblGPSPoints WHERE dateTime LIKE \'" + date[:-2] + "%\' AND LAT IS NOT NULL AND LON IS NOT NULL"
    dateTime = runQuery(query)[0]
    return dateTime

def getUniquePoints(points):
    global stayRadius
    pointsDict = {}
    for point in points:
        matchPoint = None
        for uPoint in pointsDict:
            distance = getDistance(point.lat, point.lon, uPoint.lat, uPoint.lon)
            if distance <= stayRadius:
                matchPoint = point
                matchPoint.lat = uPoint.lat
                matchPoint.lon = uPoint.lon
        if type(matchPoint) is type(None):
            pointsDict[point] = []
        else:
            if not type(pointsDict[matchPoint]) is type(None):
                pointsDict[matchPoint].append(point)
            else:
                print("it was none")
    return pointsDict

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

def processStayPoints(uniquePoints):
    global stayRadius
    query = "SELECT rowid, * FROM tblStayPoints"
    existPoints = runQuery(query)
    for stayPoint in uniquePoints:
        for existingPt in existPoints:
            if getDistance(existingPt[1], existingPt[2], stayPoint.lat, stayPoint.lon) <= stayRadius:
                stayPoint.row_id = existingPt[0]
                break
    addStayPoints(uniquePoints)

def addStayPoints(newPoints):
    conn = sqlite3.connect("GPSLogger.db")
    cur = conn.cursor()
    newCount = 0
    for stayPoint in newPoints:
        if stayPoint.row_id == -1:
            newCount += 1
            cur.execute("INSERT OR IGNORE INTO tblStayPoints VALUES (%f, %f)" % (stayPoint.lat, stayPoint.lon))
            stayPoint.row_id = cur.lastrowid
    print("%d New stay points added" %(newCount))
    conn.commit()
    cur.close()
    conn.close()
    addStayPointVisits(newPoints)

def addStayPointVisits(visitPoints):
    startTime = timer.time()
    list = []
    for stayPoint in visitPoints:
        visits = visitPoints[stayPoint]
        list.append((stayPoint.row_id, stayPoint.start, stayPoint.end))
        if not type(visits) is type(None):
            for visit in visits:
                list.append((stayPoint.row_id, visit.start, visit.end))
    runInsertMany("INSERT OR IGNORE INTO tblStayPointVisits VALUES (?,?,?)", list)
    print("%d New visits added" %(len(list)))
    aDate = getLatestVisit()[0]
    endTime = timer.time()
    addUpdate("StayPointUpdate", aDate, startTime, endTime)

def performStayPointUpdate():
    latest = getLatestUpdateTime("StayPointUpdate")
    if latest == None:
        date = "1980-01-01T00:00:00.000Z"
    else:
        date = latest
    print("Stay point update start: %s" % (latest))
    points = stayPointsAfter(date)
    uniqPoints = getUniquePoints(points)
    processStayPoints(uniqPoints)

def performJourneyUpdate():
    startTime = timer.time()
    latestUpdate = getLatestUpdateTime("JourneyUpdate")
    print("Journey update start: %s" % (latestUpdate)) 
    latestJourney = addJourneysFrom(latestUpdate)
    print("Add Journeys From Executed")
    if isinstance(latestJourney, Journey):
        endTime = timer.time()
        addUpdate("JourneyUpdate", latestJourney.end, startTime, endTime)

def addJourneysFrom(date):
    if type(date) is type(None):
        query = "SELECT rowid, * FROM tblStayPointVisits ORDER BY startTime ASC"
    else:
        query = "SELECT rowid, * FROM tblStayPointVisits WHERE strftime('%Y-%m-%dT%H:%M:%S', startTime) >  strftime('%Y-%m-%dT%H:%M:%S',\'" + str(date) + "\') ORDER BY startTime ASC"
    visits = runQuery(query)
    prevEnd = None
    journeys = []
    i = 0
    lastJourney = None
    visitsSize = len(visits)
    while i < visitsSize:
        stayID = visits[i][1]
        start = visits[i][2]
        end = visits[i][3]
        if type(prevEnd) is not type(None):
            aJourney = Journey(prevStayID, stayID, prevEnd, start)
            if aJourney.startStayPoint != aJourney.endStayPoint:
                journeys.append(aJourney)
            else:
            #	Run a further check to see if the journey furthest points is greater than the stay radius print
            #	"Rejected - Start id: %d, End id: %d, StartTime: %s. EndTime: %s" %(aJourney.startStayPoint, aJourney.endStayPoint, aJourney.start, aJourney.end)
                journeys.append(aJourney)
        prevStayID = stayID
        prevEnd = end
        i += 1
    if len(journeys) > 0:
        lastJourney = journeys[len(journeys) - 1]
        addJourneys(journeys)
        addJourneyPoints(journeys[0].start)
    return lastJourney

def addJourneys(journeys):
    journeyList = []
    for journey in journeys:
        journeyList.append((journey.startStayPoint, journey.endStayPoint, journey.start, journey.end))	
    statement = "INSERT INTO tblJourneys VALUES (?,?,?,?)"
    runInsertMany(statement, journeyList)

def addJourneyPoints(firstNewVisit):
    query = "SELECT rowid,* FROM tblJourneys WHERE strftime('%Y-%m-%dT%H:%M:%S', startTime) >= strftime('%Y-%m-%dT%H:%M:%S',\'" + firstNewVisit + "\') ORDER BY startTime ASC"
    results = runQuery(query)
    reduct = 0.0
    print("%d New journeys added" %(len(results)),) 
    for journey in results:
        rowid = journey[0]
        start = journey[3]
        end = journey[4]
        reduct += updateJourneyPoints(rowid, start, end)
    if len(results) > 0:
        print("%d%% of original journey points added" %(reduct / float(len(results)) * 100))

def updateJourneyPoints(rowid, start, end):
    global dist
    query = "SELECT Lat, Lon, \'" + str(rowid) + "\' as journeyID, rowid FROM tblGPSPoints WHERE strftime('%Y-%m-%dT%H:%M:%S', dateTime) BETWEEN strftime('%Y-%m-%dT%H:%M:%S',\'" + start + "\') AND strftime('%Y-%m-%dT%H:%M:%S',\'" + end + "\') AND LAT IS NOT NULL"
    points = runQuery(query)
    less = ramerdouglas(points, dist)
    trimmedPoints = []
    for point in less:
        journeyId = point[2]
        rowid = point[3]
        trimmedPoints.append((journeyId, rowid))
    reduct = float(len(trimmedPoints)) / float(len(points))
    insert = "INSERT INTO tblJourneyPoints VALUES (?,?)"
    runInsertMany(insert, trimmedPoints)
    return reduct
    
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

def _vec2d_dist(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

def _vec2d_sub(p1, p2):
    return (p1[0]-p2[0], p1[1]-p2[1])

def _vec2d_mult(p1, p2):
    return p1[0] * p2[0] + p1[1] * p2[1]

def ramerdouglas(line, dist):
    if len(line) < 3:
        return line

    (begin, end) = (line[0], line[-1]) if line[0] != line[-1] else (line[0], line[-2])

    distSq = []
    for curr in line[1:-1]:
        try:
            tmp = (_vec2d_dist(begin, curr) - _vec2d_mult(_vec2d_sub(end, begin), _vec2d_sub(curr, begin)) ** 2 / _vec2d_dist(begin, end))
        except:
            tmp = (_vec2d_dist(begin, curr) - _vec2d_mult(_vec2d_sub(end, begin), _vec2d_sub(curr, begin)) ** 2)
        distSq.append(tmp)

    maxdist = max(distSq)
    if maxdist < dist ** 2:
        return [begin, end]

    pos = distSq.index(maxdist)
    return (ramerdouglas(line[:pos + 2], dist) + ramerdouglas(line[pos + 1:], dist)[1:])

def removeStayPointUpdates():
    remove = "DELETE FROM tblUpdates WHERE Type = 'StayPointUpdate'"
    removeStay = "DELETE FROM tblStayPoints"
    removeVisits = "DELETE FROM tblStayPointVisits"
    runDelete(remove)
    runDelete(removeStay)
    runDelete(removeVisits)

def removeJourneyUpdates():
    remove = "DELETE FROM tblUpdates WHERE Type = 'JourneyUpdate'"
    removeJourneys = "DELETE FROM tblJourneys"
    removeJourneyPoints = "DELETE FROM tblJourneyPoints"
    runDelete(remove)
    runDelete(removeJourneys)
    runDelete(removeJourneyPoints)

def rerunUpdates():
    removeStayPointUpdates()
    removeJourneyUpdates()
    performStayPointUpdate()
    print("Stay Point Update complete")
    performJourneyUpdate()
    print("Journey Update complete")

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
	
def updateSettings(settings):
    file = open("settings.txt", 'w')
    values = "stayLength=%s||stayRadius=%s||distVal=%s||minJourney=%s" % (settings[0], settings[1], settings[2], settings[3])
    file.write(values)
    file.close()
    return True

def addError(errorType, fileName, gpsTime, errorDesc):
    runInsert("INSERT INTO tblErrors VALUES (%s, %s, %f, %s, %s)") %(errorType, fileName, timer.time(), gpsTime, errorDesc)

def writeToFile(points):
    print("%d Points writing to file" % (len(points),)) 
    gpxFile = open("../Logs/gpxOutput.gpx", 'w')
    str = "<gpx><trk><trkseg>"
    for point in points:
        str += """
		<trkpt lat=\"%s\" lon=\"%s\">
       	 	<time>%s</time>
      		</trkpt>
		""" % (point[0], point[1], point[2])
    str += "</trkseg></trk></gpx>"
    gpxFile.write(str)
    gpxFile.close()
