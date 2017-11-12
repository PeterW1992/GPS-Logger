from DBFunc import *
from Utils import *

settings = getSettings()
stayLength = settings["stayLength"]
stayRadius = settings["stayRadius"]
dist = settings["distVal"]

def stayPointsAfter(date):
    global stayRadius;global stayLength
    if type(date) is type(None):
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

def pairWithExistingStayPoints(uniquePoints):
    global stayRadius
    query = "SELECT rowid, * FROM tblStayPoints"
    existPoints = runQuery(query)
    for stayPoint in uniquePoints:
        for existingPt in existPoints:
            if getDistance(existingPt[1], existingPt[2], stayPoint.lat, stayPoint.lon) <= stayRadius:
                stayPoint.row_id = existingPt[0]
                break
    return uniquePoints

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
    return newPoints

def addStayPointVisits(visitPoints):
    list = []
    latestVisit = None
    for stayPoint in visitPoints:
        visits = visitPoints[stayPoint]
        list.append((stayPoint.row_id, stayPoint.start, stayPoint.end))
        if not type(visits) is type(None):
            for visit in visits:
                if type(latestVisit) == type(None):
                    latestVisit = visit
                elif latestVisit.end < visit.end:
                    latestVisit = visit
                list.append((stayPoint.row_id, visit.start, visit.end))
    runInsertMany("INSERT OR IGNORE INTO tblStayPointVisits VALUES (?,?,?)", list)
    print("%d New visits added" %(len(list)))
    return latestVisit
    

def performStayPointUpdate():
    startTime = timer.time()
    date = getLatestUpdateTime("StayPointUpdate")
    points = stayPointsAfter(date)
    points = getUniquePoints(points)
    points = pairWithExistingStayPoints(points)
    points = addStayPoints(points)
    lastVisit = addStayPointVisits(points)
    if type(lastVisit) != type(None):
        endTime = timer.time()
        ddUpdate("StayPointUpdate", lastVisit.end, startTime, endTime)
	
	

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
        query = "SELECT rowid, * FROM tblStayPointVisits WHERE strftime('%Y-%m-%dT%H:%M:%S', startTime) >=  strftime('%Y-%m-%dT%H:%M:%S',\'" + str(date) + "\') ORDER BY startTime ASC"
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
