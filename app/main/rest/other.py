from app.main.utils import restful, date_util
from . import rest
from flask import request
from app.main.utils import my_redis
from app.main.db.mongo import db
from app.main.utils.my_collections import OrderedSet
from boltons.setutils import IndexedSet
from datetime import datetime
import json


@rest.route("/stock/custom/definition", methods=['post'])
def stock_definition():
    """
    自定义概念
    :return:
    """
    stock_detail_set = db["stock_detail"]
    tag_set = db["concept_tag"]

    params: dict = request.json
    code = params.get("code", None)

    if code is None:
        name = params.get("name", None)
        stock_detail = stock_detail_set.find_one({"name": name})
    else:
        stock_detail = stock_detail_set.find_one({"code": code})

    tags: list = params.get("tags")
    is_overdue = params.get("isOverwrite", False)

    custom: list = stock_detail.get('custom', [])

    rets = [prev for prev in custom if prev not in tags]
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
    # 添加标签关联
    for tag in tags:
        group = group_dict.get(tag, {})
        group['name'] = tag
        group['update'] = datetime.now()
        relate_name = group.get("relate_name", [])
        relate_code = group.get("relate_code", [])
        if name not in relate_name:
            relate_name.append(name)
        if code not in relate_code:
            relate_code.append(code)

        group['relate_name'] = relate_name
        group['relate_code'] = relate_code

        tag_set.update({"name": tag}, {"$set": group}, upsert=True)

    # 删除标签的时候,把关联也去除
    for ret in rets:
        group = group_dict.get(ret, {})
        group['name'] = ret
        group['update'] = datetime.now()
        relate_name = group.get("relate_name", [])
        relate_code = group.get("relate_code", [])
        if name in relate_name:
            relate_name.remove(name)
        if code in relate_code:
            relate_code.remove(code)

        group['relate_name'] = relate_name
        group['relate_code'] = relate_code

        if len(relate_code) != 0:
            tag_set.update({"name": ret}, {"$set": group}, upsert=True)
        else:
            tag_set.delete_one({"name": ret})

    # 记录工作点位
    my_work = db['my_work']
    definition_work = my_work.find_one({"name": "definition"})

    definition_work = definition_work if definition_work is not None else {}
    latest = definition_work.get("latest", None)
    current = definition_work.get("current", None)

    if name != current:
        new_work_info = dict(current=name, latest=current)
        my_work.update_one({"name": "definition"}, {"$set": new_work_info}, upsert=True)

    return restful.response("ok")


@rest.route("/stock/custom/tags", methods=['get'])
def get_custom_tags():
    """
    获取所有自定义的标签
    :return:
    """
    tag_set = db["concept_tag"]
    tag_list = list(tag_set.find({}))

    tags = [tag['name'] for tag in tag_list]

    return restful.response(tags)


@rest.route("/stock/custom/progress", methods=['get'])
def get_work_info():
    """
    获取自定义标签工作的进展
    :return:
    """
    my_work = db['my_work']
    definition_work = my_work.find_one({"name": "definition"})

    tag_set = db["concept_tag"]
    tag_list = list(tag_set.find({}))

    # 编辑过的个股和标签
    tag_size = len(tag_list)

    edited_stock = set()
    edited_stock_name = dict()
    for tag in tag_list:
        edited_stock.update(tag['relate_code'])
        edited_stock_name.update({name: 1 for name in tag['relate_name']})
    edited_stock_size = len(edited_stock)

    definition_work['tag_size'] = tag_size
    definition_work['edited_stock_size'] = edited_stock_size

    my_work.update_one({"name": "definition"}, {"$set": definition_work}, upsert=True)

    tag_table = [{tag['name']: len(tag['relate_code'])} for tag in tag_list]
    definition_work['table'] = tag_table

    now = date_util.get_latest_work_day()
    # 提前设置好的请求参数
    stock_remind_record = db['stock_remind_record']

    result = stock_remind_record.find_one({"date": date_util.get_start_of_day(now), "key": "trend_reversal"})
    recommend_stock_set = set()
    for r in result['boards']:
        recommend_stock_set.update([stock['name'] for stock in r['stocks']])

    recommend = [name for name in list(recommend_stock_set) if name not in edited_stock_name.keys()]

    definition_work['recommend'] = recommend[0:5]
    return restful.response(definition_work)
