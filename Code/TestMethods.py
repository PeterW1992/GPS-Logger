# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
from collections import Counter

def getTotalDistance(allPoints):
    if len(allPoints) > 0:
        totalDistance = 0
        for i in range(len(allPoints)):
            if i + 1 < len(allPoints):
                lat1 = float(allPoints[i][0])
                lon1 = float(allPoints[i][1])
                lat2 = float(allPoints[i + 1][0])
                lon2 = float(allPoints[i + 1][1])
                totalDistance += getDistance(lat1, lon1, lat2, lon2)
                return totalDistance
            else:
                return 0
            
def stayPointsAfterOld(date):
    if len(date) == 0:
        query = "SELECT * FROM tblGPSPoints WHERE SPEED < 0.5 AND MODE = 3 ORDER BY dateTime ASC"
    else:
        query = "SELECT * FROM tblGPSPoints WHERE SPEED < 0.5 AND MODE = 3 AND strftime('%Y-%m-%dT%H:%M:%S', dateTime) > strftime('%Y-%m-%dT%H:%M:%S',\'" + str(date) + "\') ORDER BY dateTime ASC"
    points = runQuery(query)
    stayPoints = []; stayPointList = []
    for point in points:
        date = getDateTime(point[2])
        if len(stayPointList) != 0:
            prevDate = stayPointList[len(stayPointList) - 1][2]
            secondsDiff = (date - prevDate).total_seconds()
            if secondsDiff > 2:
                diffFirstLast = (stayPointList[len(stayPointList) - 1][2] - stayPointList[0][2]).total_seconds()
                if diffFirstLast > 1000:
                    prevLat = 0; prevLon = 0; distanceTotal = 0; latsRounded = []; lonsRounded = []
                    for stayPoint in stayPointList:
                        latsRounded.append(round(stayPoint[0], 5))
                        lonsRounded.append(round(stayPoint[1], 5))
                        distanceTotal += getDistance(stayPoint[0], stayPoint[1], prevLat, prevLon)
                        prevLat = stayPoint[0]
                        prevLon = stayPoint[1]
                    latCounter = Counter(latsRounded); lonCounter = Counter(lonsRounded)		
                    latMax = max(latCounter.values()); lonMax = max(lonCounter.values()); count = len(stayPointList)
                    latAvg = [k for k, v in latCounter.items() if v == latMax][0]
                    lonAvg = [k for k, v in lonCounter.items() if v == lonMax][0]
                    averageDistance = distanceTotal / count
                    if averageDistance < 10000:
                        start = stayPointList[0][2].isoformat()
                        end = stayPointList[len(stayPointList) - 1][2].isoformat()
                        stayPoint = StayPoint(latAvg, lonAvg, start, end)
                        stayPoints.append(stayPoint)
                        stayPointList = []
                        continue
                    else:
                        print("%s, %s AVG Distance to great %s") % (latAvg, lonAvg, str(averageDistance))
                    stayPointList = []
        stayPointList.append((point[0], point[1], date))
    return stayPoints

def stayPointsAfterTest(date):
    global stayRadius;global stayLength
    if len(date) == 0:
        query = "SELECT *, rowid FROM tblGPSPoints WHERE LAT IS NOT NULL AND dateTime is not NULL GROUP BY strftime('%Y-%m-%dT%H:%M', dateTime) ORDER BY dateTime ASC"
    else:
        query = "SELECT *, rowid FROM tblGPSPoints WHERE LAT IS NOT NULL AND strftime('%Y-%m-%dT%H:%M:%S', dateTime) > strftime('%Y-%m-%dT%H:%M:%S',\'" + date + "\') GROUP BY strftime('%Y-%m-%dT%H:%M', dateTime) ORDER BY dateTime ASC"
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
                print("Stay point found: " + str(prevDate))
                startMinute = prevDate.replace(microsecond=0).isoformat()
                endMinute = date.replace(microsecond=0).isoformat()
                startPoint = getPointInMinute("MAX", startMinute)
                endPoint = points[i]
                actualEndPt = getStayEndPoint(prevPoint, points[i:]) #Using an array of points from this point find the point where they leave the radius..
					
                # if  mostRecentPoint
                if type(startPoint) is not type(None) and type(endPoint) is not type(None) and type(actualEndPt) is not type(None):
                    start = startPoint[2]
                    end = actualEndPt[2]
                    lat1 = startPoint[0];lon1 = startPoint[1];lat2 = endPoint[0];lon2 = endPoint[1]
                    distance = getDistance(lat1, lon1, lat2, lon2)
                    # found end/start of end of stay point, need to find start of journey
                    if distance <= stayRadius:
                        stayPoints.append(StayPoint(lat1, lon1, start, end))
                    else:
                        print("Distance to great: %s") % str(distance)
                else:
                    print("Start or end visit date time was null")
        prevPoint = points[i]
        i += 1
    return stayPoints

def getStayEndPoint(stayPoint, points):
    global stayRadius
    i = 0
    size = len(points)
    returnPoint = None
    while i < size:
        point = points[i]
        ptLat = point[0];ptLon = point[1]
        stLat = stayPoint[0];stLon = stayPoint[1]
        if getDistance(ptLat, ptLon, stLat, stLon) >= stayRadius:
            if i - 1 > 0:
                par = points[i-1]
            else:
                par = points[i]
            query = "SELECT * FROM tblGPSPoints WHERE strftime('%Y-%m-%dT%H:%M', dateTime) = strftime('%Y-%m-%dT%H:%M',\'" + par[2] + "\') AND LAT IS NOT NULL AND LON IS NOT NULL ORDER BY dateTime ASC"
            narrPoints = runQuery(query)
            i2 = 0
            narrSize = len(narrPoints)
            while i2 < narrSize:
                if getDistance(narrPoints[i2][0], narrPoints[i2][1], stLat, stLon) >= stayRadius:
                    return narrPoints[i2]
                i2 += 1
        i += 1
    return None
