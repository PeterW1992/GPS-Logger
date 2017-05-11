import sqlite3

conn = sqlite3.connect('GPSLogger.db')
cur = conn.cursor()

tblGPSP = "tblGPSPoints"
tblSP = "tblStayPoints"
tblSPV = "tblStayPointVisits"
tblJs = "tblJourneys"
tblUpdates = "tblUpdates"

lat = "Lat REAL,"
lon = " Lon REAL,"
dateTime = " DateTime TEXT PRIMARY KEY,"
alt = " Alt REAL,"
speed = " Speed REAL,"
epx = " Epx REAL,"# Estimate error in lon
epy = " Epy REAL,"# Estimate error in lat
epz = " Epz REAL," # Estimate error in alt
ept = " Ept REAL," # Estimate error in time
mode = " Mode INTEGER,"
track = " Track REAL" # Course over ground, degrees from true north. 

# tblStayPoints columns
stayPointLon = " Lon REAL"

# tblStayPointVisits columns
stayPointId = " StayPointID INTEGER,"
startTime = " StartTime TEXT,"
endTime = " EndTime TEXT,"
stayPointFK = " PRIMARY KEY(StartTime,EndTime), FOREIGN KEY (stayPointID) REFERENCES %s(ROWID)" % (tblSPV)

# tblJourneys columns
startStayPoint = " StartStayPoint INTEGER,"
endStayPoint = " EndStayPoint INTEGER,"
startPointPKFK = " PRIMARY KEY (StartTime) FOREIGN KEY (startStayPoint) REFERENCES %s(ROWID)," % (tblSP)
endPointFK = " FOREIGN KEY (endStayPoint) REFERENCES %s(ROWID)" % (tblSP)

# tblUpdate columns
updateType = " Type TEXT,"
updateDT = " DateTime TEXT,"
updateStart = " StartTime REAL,"
updateEnd = " EndTime REAL"

createTb11 = "CREATE TABLE %s (%s %s %s %s %s %s %s %s %s %s %s)" % (tblGPSP, lat, lon, dateTime, alt, speed, epx, epy, epz, ept, mode, track)
createTbl2 = "CREATE TABLE %s (%s %s)" % (tblSP, lat, stayPointLon)
createTbl3 = "CREATE TABLE %s (%s %s %s %s)" % (tblSPV, stayPointId, startTime, endTime, stayPointFK)
createTbl4 = "CREATE TABLE %s (%s %s %s %s %s %s)" % (tblJs, startStayPoint, endStayPoint, startTime, endTime, startPointPKFK, endPointFK)
createTbl5 = "CREATE TABLE %s (%s %s %s %s)" % (tblUpdates, updateType, updateDT, updateStart, updateEnd)
createTbl6 = "CREATE TABLE tblJourneyPoints (JourneyId INTEGER, pointID INTEGER, PRIMARY KEY (pointID) FOREIGN KEY (JourneyID) REFERENCES tblJourneys(ROWID), FOREIGN KEY (pointID) REFERENCES tblGPSPoints(ROWID))"

#cur.execute(createTbl1)
#cur.execute(createTbl2)
#cur.execute(createTbl3)
#cur.execute(createTbl4)
cur.execute(createTbl5)
#cur.execute(createTbl6)

conn.commit()
cur.close()
conn.close()
