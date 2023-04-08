from datetime import datetime
from typing import Dict

from app.main.model import Basic
from app.main.model.echart import YAxisDesc, YAxisData


class BoardValue(Basic):
    value: Dict # 结果集
    date: datetime # 时间点


class BoardValueEchart(Basic):
    y_axis_desc: YAxisDesc
    y_axis_data: YAxisData
