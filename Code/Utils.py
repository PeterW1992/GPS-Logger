import datetime as dt
import logging
import math
import os

loggingFileName = 'GPSLogger_' + dt.datetime.now().strftime('%Y_%m_%d') + '.log'
logging.basicConfig(filename=loggingFileName, format='%(asctime)s %(message)s', encoding='utf-8', level=logging.DEBUG)

logging.info('Test Log')
logging.info('Test Log again')

PI = math.pi

def toRadians(x):
    return x * PI / 180

def getDistance(lat1, lon1, lat2, lon2):
    R = 6371e3
    p1 = toRadians(lat1)
    p2 = toRadians(lat2)
    trip = toRadians(lat2-lat1)
    trih = toRadians(lon2-lon1)
    a = math.sin(trip / 2) * math.sin(trip / 2) + math.cos(p1) * math.cos(p2) * math.sin(trih / 2) * math.sin(trih / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def getDateTime(dateTime):
    return dt.datetime.strptime(dateTime, "%Y-%m-%dT%H:%M:%S.%fZ")

def getDBFileSize():
    fileSize = float(os.path.getsize("GPSLogger.db"))
    return fileSize / 1024 / 1024

def readableFromTimeStamp(tStamp):
	return dt.datetime.fromtimestamp(tStamp).strftime('%Y-%m-%d %H:%M:%S')

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
	
def updateSettings(settings):
    file = open("settings.txt", 'w')
    values = "stayLength=%s||stayRadius=%s||distVal=%s||minJourney=%s" % (settings[0], settings[1], settings[2], settings[3])
    file.write(values)
    file.close()
    return True

def extractReportData(report):
    mode = None; lon = None; lat = None; dateTime = None; epx = None; epy = None; epv = None; ept = None; speed = None; alt = None; track = None
    if hasattr(report, 'mode'):
        mode = report.mode
    if hasattr(report, 'time'):
        if str(report.time)[0:4] != "1980":
            dateTime = str(report.time)
        if type(mode) is not type(None) and mode == 3 and type(dateTime) is not type(None):
            if hasattr(report, 'lon'):
                lon = report.lon
            if hasattr(report, 'lat'):
                lat = report.lat
            if hasattr(report, 'time'):
                dateTime = str(report.time)
            if hasattr(report, 'epx'):
                epx = report.epx
            if hasattr(report, 'epy'):
                epy = report.epy
            if hasattr(report, 'epv'):
                epv = report.epv
            if hasattr(report, 'ept'):
                ept = report.ept
            if hasattr(report, 'speed'):
                speed = report.speed
            if hasattr(report, 'alt'):
                alt = report.alt
            if hasattr(report, 'track'):
                track = report.track
            asTuple = (lat, lon, dateTime, alt, speed, epx, epy, epv, ept, mode, track)
            return asTuple
    return None

