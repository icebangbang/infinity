import json
from typing import List, Dict

from app.main.model import Basic
from app.main.model.echart import YAxisDesc, YAxisData


class RelateStock(Basic):
    code: str
    name: str
    rate: float


class RecommendEtf(Basic):
    fund_code: str
    fund_name: str
    y_axis_desc: YAxisDesc
    y_axis_data: YAxisData
    relate_stocks: List[RelateStock]


if __name__ == '__main__':
    r = RecommendEtf(fund_code=123, fund_name=666)
    y_axis_desc = r.y_axis_desc
    print(json.dumps(r))
