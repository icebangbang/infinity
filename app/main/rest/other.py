from app.main.utils import restful
from . import rest
from flask import request
from app.main.utils import my_redis
from app.main.db.mongo import db
from app.main.utils.my_collections import OrderedSet
from boltons.setutils import IndexedSet
from datetime import datetime


@rest.route("/stock/custom/definition", methods=['post'])
def stock_definition():
    stock_detail_set = db["stock_detail"]
    tag_set = db["concept_tag"]

    params: dict = request.json
    code = params.get("code", None)

    if code is None:
        name = params.get("name", None)
        stock_detail = stock_detail_set.find_one({"name": name})
    else:
        stock_detail = stock_detail_set.find_one({"code": code})

    tags:list = params.get("tags")
    is_overdue = params.get("isOverwrite", False)

    custom: list = stock_detail.get('custom', [])

    rets = [ prev for prev in custom if prev not in tags ]
    total = tags.copy()
    total.extend(rets)

    if is_overdue:
        custom = tags
    else:
        custom.extend(tags)
    stock_detail['custom'] = list(IndexedSet(custom))
    stock_detail_set.update_one({"code": stock_detail['code']}, {"$set": stock_detail}, upsert=True)

    tag_group = list(tag_set.find({"name": {"$in": total}}))
    group_dict = {group['name']: group for group in tag_group}

    name = stock_detail['name']
    code = stock_detail['code']
    for tag in tags:
        group = group_dict.get(tag, {})
        group['name'] = tag
        group['update'] = datetime.now()
        relate_name = group.get("relate_name",[])
        relate_code = group.get("relate_code",[])
        if name not in relate_name:
            relate_name.append(name)
        if code not in relate_code:
            relate_code.append(code)

        group['relate_name'] = relate_name
        group['relate_code'] = relate_code

        tag_set.update({"name": tag}, {"$set": group}, upsert=True)

    for ret in rets:
        group = group_dict.get(ret, {})
        group['name'] = ret
        group['update'] = datetime.now()
        relate_name = group.get("relate_name",[])
        relate_code = group.get("relate_code",[])
        if name in relate_name:
            relate_name.remove(name)
        if code in relate_code:
            relate_code.remove(code)

        group['relate_name'] = relate_name
        group['relate_code'] = relate_code

        if len(relate_code) !=0:
            tag_set.update({"name": ret}, {"$set": group}, upsert=True)
        else:
            tag_set.delete_one({"name":ret})

    return restful.response("ok")


@rest.route("/stock/custom/tags", methods=['get'])
def get_custom_tags():
    tag_set = db["concept_tag"]
    tag_list = list(tag_set.find({}))

    tags = [tag['name'] for tag in tag_list]

    return restful.response(tags)
