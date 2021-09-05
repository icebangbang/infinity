import pymongo
import pytz

tzinfo = pytz.timezone('Asia/Shanghai')
myclient = pymongo.MongoClient("mongodb://admin:123456@101.37.24.40:20017/")
db = myclient["stock"]
