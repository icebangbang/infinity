import pymongo
import pytz

tzinfo = pytz.timezone('Asia/Shanghai')
myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
db = myclient["stock"]