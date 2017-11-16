from Utils import *
from DBFunc import *

stayPoints = runQuery("SELECT * FROM tblStayPointVisits ORDER BY startTime")

for stayPoint in stayPoints:
    print(stayPoint)

journeys = runQuery("SELECT * FROM tblJourneys ORDER BY startTime")

for journey in journeys:
    print(journey)

#gpsPoints = runQuery("SELECT * FROM tblGPSPoints WHERE dateTime LIKE \'2017-11-15%\'");
#writeToFile(gpsPoints)
