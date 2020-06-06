from tinydb import TinyDB, Query
import datetime

db = TinyDB('./database.json')

def getToday():
    return datetime.datetime.now()

def get2DaysAgo():
    return getToday() - datetime.timedelta(days=2)

def isOld(date):
    date_d = int(date.split('-')[2])
    date_m = int(date.split('-')[1])
    date_y = int(date.split('-')[0])
    date = datetime.datetime(date_y, date_m, date_d)
    twoDaysAgo = get2DaysAgo()
    return date <= twoDaysAgo

def clean():
    removed = 0
    for item in db:
        timestamp = item['timestamp']
        filename = item['filename']
        user = item['user']
        element = Query()
        if isOld(timestamp):
            removed += 1
            db.remove(element['filename'] == filename and element['user'] == user and element['timestamp'] == timestamp)
    print('Database cleaned! {} elements removed'.format(removed))