from DBFunc import *
from Utils import *
from UpdateMethods import *
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

#performStayPointUpdate()
#performJourneyUpdate()
#rerunUpdates()

#query = "SELECT * FROM tblGPSPoints WHERE strftime('%Y-%m-%dT%H:%M:%S', dateTime) BETWEEN strftime('%Y-%m-%dT%H:%M:%S',\'" + start + "\') AND strftime('%Y-%m-%dT%H:%M:%S',\'" + end + "\')"
#points = runQuery(query)
#writeToFile(points)

query = "SELECT *, endTime - startTime AS Seconds FROM tblUpdates ORDER BY Type, dateTime ASC"
records = runQuery(query)
recordsAmount = len(records)
i = 0
while i < recordsAmount:
    record = records[i]
    print("Type: %s, Time: %s, Duration: %d" %(record[0], record[1], record[4]))
#    print("Type: %s, Time: %s, Duration: %d" %(record[0], getDateTime(record[1]), record[4]))
    i += 1

print("--------------------------------------------------------------")

tAfter = timer.time()
totalTime = tAfter - tBefore
print("Test Runtime: " + str(totalTime) + "s")

print("----------------------------Errors----------------------------")
errors = runQuery("SELECT * FROM tblErrors")
for err in errors:
    readable = readableFromTimeStamp(err[2])
    print("%s, %s, %s, %s, %s" %(err[0], err[1], readable, err[3], err[4]))
