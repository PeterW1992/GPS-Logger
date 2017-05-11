from DBFunc import *
from Utils import *
import time as timer

#dbFields = ["Lat", "Lon", "DateTime", "Alt", "Speed", "Epx", "Epy", "Epz", "Ept", "Mode", "Track"]

settings = getSettings()
stayLength = settings["stayLength"]
stayRadius = settings["stayRadius"]
dist = settings["distVal"]

fileSize = getDBFileSize()
gpsPointCount = getRecordCountFor("tblGPSPoints")
stayPointCount = getRecordCountFor("tblStayPoints")
stayVisitsCount = getRecordCountFor("tblStayPointVisits")
journeyCount = getRecordCountFor("tblJourneys")
journeyPointCount = getRecordCountFor("tblJourneyPoints")

print("GPS Point count: %d" % (gpsPointCount, ))
print("Stay point count: %d" % (stayPointCount, ))
print("Stay visits count: %d" % (stayVisitsCount, )) 
print("Journey count: %d" % (journeyCount, )) 
print("Journey point count: %d" % (journeyPointCount, ))
print("Hours recorded: " + str(gpsPointCount / 60 / 60))
print("Database size (MB): " + str(fileSize))
firstRecord = getOldestDateTime()
lastRecord = getLatestDateTime()
print("Oldest point: " + str(firstRecord))
print("Most recent point: " + str(lastRecord))
print(getLatestVisitStr())
print(getLatestJourneyStr())
tBefore = timer.time()
print("\n-------------------------Test Outputs-------------------------")

#rerunUpdates()

#performJourneyUpdate()
start = "2017-05-10T00:00:00"
end = "2017-05-11T00:00:00"
query = "SELECT * FROM tblGPSPoints WHERE strftime('%Y-%m-%dT%H:%M:%S', dateTime) BETWEEN strftime('%Y-%m-%dT%H:%M:%S',\'" + start + "\') AND strftime('%Y-%m-%dT%H:%M:%S',\'" + end + "\')"
points = runQuery(query)
writeToFile(points)

query = "SELECT *, endTime - startTime AS Seconds FROM tblUpdates"
records = runQuery(query)
for record in records:
    print(record)

#removeStayPointUpdates()
#removeJourneyUpdates()
#runDelete("DROP TABLE tblUpdates")
#import CreateTables

print("--------------------------------------------------------------")

tAfter = timer.time()
totalTime = tAfter - tBefore
print("Test Runtime: " + str(totalTime) + "s")
