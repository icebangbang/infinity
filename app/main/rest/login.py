from app.main.utils import restful, encryption, simple_util
from . import rest
from app.main.task import demo
from app.main.task import board_task
from flask import request
from app.main.utils import my_redis


@rest.route("/currentUser", methods=['get'])
def current_user():
    token = request.args.get("token")
    if simple_util.is_empty(token): return restful.status_response("fail")
    r = {
        "name": "Serati Ma",
        "avatar": "https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png",
        "userid": "00000001",
        "email": "antdesign@alipay.com",
        "signature": "海纳百川，有容乃大",
        "title": "交互专家",
        "group": "蚂蚁金服－某某某事业群－某某平台部－某某技术部－UED",
        "tags": [
            {
                "key": "0",
                "label": "很有想法的"
            },
            {
                "key": "1",
                "label": "专注设计"
            },
            {
                "key": "2",
                "label": "辣~"
            },
            {
                "key": "3",
                "label": "大长腿"
            },
            {
                "key": "4",
                "label": "川妹子"
            },
            {
                "key": "5",
                "label": "海纳百川"
            }
        ],
        "notifyCount": 12,
        "unreadCount": 11,
        "country": "China",
        "access": "admin",
        "geographic": {
            "province": {
                "label": "浙江省",
                "key": "330000"
            },
            "city": {
                "label": "杭州市",
                "key": "330100"
            }
        },
        "address": "西湖区工专路 77 号",
        "phone": "0752-268888888"
    }
    return restful.response_obj(dict(data=r))


@rest.route("/login/account", methods=['post'])
def login():
    params: dict = request.json
    username = params.get("username")
    type = params.get("type")
    password = params.get("password")

    if password == 'jjk':
        r = dict(currentAuthority="admin", status='ok', type='account',token=encryption.aes_encrypt("{}_{}".format(username,type)))
        return restful.response_obj(r)
    return restful.response_obj(dict(status='fail'))
