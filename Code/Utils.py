import datetime as dt
import math
import os

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


