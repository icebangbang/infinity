from app.main.utils import date_util
from . import rest
from app.main.utils import restful
from app.main.utils import simple_util
from flask import request
from app.main.db.mongo import db
from datetime import datetime


@rest.route("/ppi", methods=['get'])
def get_ppi():
    start = datetime(2008, 1, 1)
    ppi = db['ppi']
    ppi_list = list(ppi.find({"date": {"$gte": start}}).sort("_id", -1))

    cpi = db['cpi']
    cpi_list = list(cpi.find({"date": {"$gte": start}}).sort("_id", -1))

    date = []
    current = []
    grace = []
    accum = []
    cpi = []

    for i, p in enumerate(ppi_list):
        date.append(date_util.date_time_to_str(p['date'], fmt='%Y-%m'))
        current.append(float(p['current']))
        grace.append(float(p['grace']))
        accum.append(float(p['accum']))
        cpi.append(float(cpi_list[i]['country_current']))

    return restful.response(data=dict(date=date, current=current, grace=grace, accum=accum, cpi=cpi))


@rest.route("/sow", methods=['get'])
def get_sow_data():
    pig_data = db['pig_data']
    sow_data_list = list(pig_data.find({"name": "能繁母猪存栏"}).sort("_id", 1))

    num = []
    tb = []
    hb = []
    date = []
    for i, sow in enumerate(sow_data_list):
        num.append(sow["num"])
        tb.append(sow["tb"].strip('%'))
        hb.append(sow["hb"].strip('%'))
        date.append(date_util.date_time_to_str(sow['date'], fmt='%Y-%m'))
    return restful.response(data=dict(date=date, num=num, tb=tb, hb=hb))