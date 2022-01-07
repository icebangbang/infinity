import pymongo
import logging

myclient = pymongo.MongoClient("mongodb://root:whosyourdaddy$879@39.105.104.215:20017/")
db = myclient['stock']

def init_db(app):
    myclient = pymongo.MongoClient(app.config['MONGO_URL'])
    db = myclient['stock']
    return db


