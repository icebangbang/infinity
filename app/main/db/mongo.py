import pymongo
import pytz

tzinfo = pytz.timezone('Asia/Shanghai')
myclient = pymongo.MongoClient("mongodb://172.16.1.184:27017/")
db = myclient["stock"]