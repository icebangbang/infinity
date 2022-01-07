import pymongo
import pytz

tzinfo = pytz.timezone('Asia/Shanghai')
# myclient = pymongo.MongoClient("mongodb://admin:whosyourdaddy$879@172.16.1.184:27017/")
myclient = pymongo.MongoClient("mongodb://root:whosyourdaddy$879@172.17.156.159:20017/")
db = myclient["stock"]


