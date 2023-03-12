from typing import List

from app.main.model import Basic
from app.main.model.echart import YAxisData, YAxisDesc, Legend


class ResponseBody(Basic):
    x: List[any]  # x轴数据
    y_array: List[YAxisData]  # y轴数据
    desc: str  # 板块描述信息
    multiSeries: bool  # 是否对数据集响应
    totalStock: int  # 包含的个股数
    yAxis_array: List[YAxisDesc]    # y轴描述信息
    legend: Legend # 图例相关嘻嘻
