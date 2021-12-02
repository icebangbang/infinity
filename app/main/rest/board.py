from app.main.utils import restful
from . import rest
from app.main.task import demo
from app.main.task import board_task
from app.main.db.mongo import db


@rest.route("/board", methods=['get'])
def get_board():
    set = db["board_k_line"]

    latest = set.find_one({},sort=[("date", -1)])
    date = latest['date']

    total = list(set.find({"date":date,"type":2}))

    return restful.response(total)

