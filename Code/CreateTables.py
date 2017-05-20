import sqlite3

conn = sqlite3.connect('GPSLogger.db')
cur = conn.cursor()

tblGPSP = "tblGPSPoints"
tblSP = "tblStayPoints"
tblSPV = "tblStayPointVisits"
tblJs = "tblJourneys"
tblUpdates = "tblUpdates"
tblErrors = "tblErrors"

lat = "Lat REAL"; lon = " Lon REAL"; dateTime = " DateTime TEXT PRIMARY KEY"; alt = " Alt REAL"; speed = " Speed REAL"; 
epx = " Epx REAL"; epy = " Epy REAL"; epz = " Epz REAL"; ept = " Ept REAL"; mode = " Mode INTEGER"; track = " Track REAL" 

# tblStayPointVisits columns
stayPointId = " StayPointID INTEGER"; startTime = " StartTime TEXT"; endTime = " EndTime TEXT"
stayPointPKFK = " PRIMARY KEY(StartTime,EndTime) FOREIGN KEY (stayPointID) REFERENCES %s(ROWID)" % (tblSPV)

# tblJourneys columns
startStayPoint = " StartStayPoint INTEGER"; endStayPoint = " EndStayPoint INTEGER";
startPointPKFK = " PRIMARY KEY (StartTime) FOREIGN KEY (startStayPoint) REFERENCES %s(ROWID)," % (tblSP); endPointFK = " FOREIGN KEY (endStayPoint) REFERENCES %s(ROWID)" % (tblSP)

# tblUpdate columns
updateType = " Type TEXT"; updateDT = " DateTime TEXT"; updateStart = " StartTime REAL"; updateEnd = " EndTime REAL"

# tblErrors columns
errorType = " Type TEXT"; fileName = " File TEXT"; sysTime = " SystemTime TEXT"; gpsTime = " gpsTime TEXT"; errorDesc = " ErrorDesc TEXT"

createTb11 = "CREATE TABLE %s (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (tblGPSP, lat, lon, dateTime, alt, speed, epx, epy, epz, ept, mode, track)
createTbl2 = "CREATE TABLE %s (%s, %s)" % (tblSP, lat, lon)
createTbl3 = "CREATE TABLE %s (%s, %s, %s, %s)" % (tblSPV, stayPointId, startTime, endTime, stayPointPKFK)
createTbl4 = "CREATE TABLE %s (%s, %s, %s, %s, %s, %s)" % (tblJs, startStayPoint, endStayPoint, startTime, endTime, startPointPKFK, endPointFK)
createTbl5 = "CREATE TABLE %s (%s, %s, %s, %s,)" % (tblUpdates, updateType, updateDT, updateStart, updateEnd)
createTbl6 = "CREATE TABLE tblJourneyPoints (JourneyId INTEGER, pointID INTEGER, PRIMARY KEY (pointID) FOREIGN KEY (JourneyID) REFERENCES tblJourneys(ROWID), FOREIGN KEY (pointID) REFERENCES tblGPSPoints(ROWID))"
createTbl7 = "CREATE TABLE %s (%s, %s, %s, %s, %s)" %(tblErrors, errorType, fileName, sysTime, gpsTime, errorDesc)

#cur.execute(createTbl1)
#cur.execute(createTbl2)
#cur.execute(createTbl3)
#cur.execute(createTbl4)
#cur.execute(createTbl5)
#cur.execute(createTbl6)
#cur.execute(createTbl7)

conn.commit()
cur.close()
conn.close()
