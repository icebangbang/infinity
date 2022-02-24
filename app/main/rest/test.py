from app.main.utils import restful
from . import rest
from app.main.task import demo
from app.main.task import board_task
from flask import request
from app.main.utils import my_redis


@rest.route("/test/", methods=['get'])
def current_user():
    r = {
        "200": {
            "description": "Success",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/CurrentUser"
                    }
                }
            }
        }
    }
    return restful.response_obj(r)
