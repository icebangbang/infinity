import pymongo
import pytz

tzinfo = pytz.timezone('Asia/Shanghai')
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["stock"]
