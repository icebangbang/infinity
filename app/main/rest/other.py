from app.main.utils import restful
from . import rest
from flask import request
from app.main.utils import my_redis
from app.main.db.mongo import db
from app.main.utils.my_collections import OrderedSet
from boltons.setutils import IndexedSet


@rest.route("/stock/custom/definition", methods=['post'])
def stock_definition():
    stock_detail_set = db["stock_detail"]

    params: dict = request.json
    code = params.get("code", None)

    if code is None:
        name = params.get("name", None)
        stock_detail = stock_detail_set.find_one({"name": name})
    else:
        stock_detail = stock_detail_set.find_one({"code": code})

    definition = params.get("definition")
    is_overdue = params.get("is_overwrite", False)

    custom: list = stock_detail.get('custom', [])

    if is_overdue:
        custom = definition
    else:
        custom.extend(definition)
    stock_detail['custom'] = list(IndexedSet(custom))
    stock_detail_set.update_one({"code": stock_detail['code']}, {"$set": stock_detail}, upsert=True)

    return restful.response("ok")
