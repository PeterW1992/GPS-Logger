from Utils import *
from DBFunc import *

stayPoints = runQuery("SELECT * FROM tblStayPointVisits WHERE StartTime LIKE \'2017-11-10%\' ORDER BY startTime")

for stayPoint in stayPoints:
    print(stayPoint)

#gpsPoints = runQuery("SELECT * FROM tblGPSPoints WHERE dateTime LIKE \'2017-11-10%\'");
#writeToFile(gpsPoints)
