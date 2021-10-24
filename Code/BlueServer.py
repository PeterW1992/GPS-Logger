from bluetooth import *
from DBFunc import *
from Utils import *
import logging
from datetime import datetime
import json

server_sock = None
port = None
uuid = None
client_sock = None
client_info = None

loggingFileName = 'BlueServer_' + datetime.now().strftime('%Y_%m_%d') + '.log'
logging.basicConfig(filename=loggingFileName, format='%(asctime)s %(message)s', encoding='utf-8', level=logging.DEBUG)

def setUp():
    global server_sock
    global port
    global uuid
    global advertise_service
    global client_sock
    global server_sock
    server_sock = BluetoothSocket(RFCOMM)
    server_sock.bind(("", PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    advertise_service(server_sock, "TrackerServer",
                      service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE], )
    print "Waiting for connection on RFCOMM channel %d" % port
    client_sock, client_info = server_sock.accept()
    print "Accepted connection from ", client_info
setUp()
try:
    while True:
	data = client_sock.recv(1024)
	returnString = ""
	print(data)
	dataJson = json.loads(data)
	command = dataJson["cmd"]
	print "received command: %s" % command
	client_sock.send("")

	if command == "getDataAfter":
            visitDate = dataJson["p1"]
            journeyDate = dataJson["p2"]
            arrayReturn = {}
            arrayReturn['stayPoints'] = getStayPoints()
            arrayReturn['stayVisits'] = getVisitsAfter(visitDate)
            journeys = getJourneysAfter(journeyDate)
            arrayReturn['journeys'] = journeys
            arrayReturn['journeyPoints'] = getJourneyPoints(journeys)
            arrayReturn['loggerStatus'] = getSummary()
            points = arrayReturn

	if command == "getJourneysAfter":
            date = dataJson["p1"]
            points = getJourneysAfter(date)
	
	if command == "getSettings":
            points = getSettings()

	if command == "updateSettings":
            i = 1
            values = []
            paramsSize = len(dataJson)
            while i < paramsSize:
                values.append(dataJson["p" + str(i)])
                i += 1
            points = [(updateSettings(values), )]
	
	print(str(len(points)) + " Points being returned")
	client_sock.send(str(json.dumps(points) + "EndOfTransmission"))

	print "Data posted"
	client_sock.close()
	server_sock.close()
	setUp()
	
except IOError:
    logging.error("IOError in BlueServer.py")
    pass

except KeyboardInterrupt:
    print "disconnected"
    client_sock.close()
    server_sock.close()

client_sock.close()
server_sock.close()

print "disconnected"
