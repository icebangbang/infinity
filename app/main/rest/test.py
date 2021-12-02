from app.main.utils import restful
from . import rest
from app.main.task import demo
from app.main.task import board_task


@rest.route("/t", methods=['get'])
def send_job():
    demo.parent.delay(10)

    return restful.response("ok")
