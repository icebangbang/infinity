"""
获取股市移动数据
"""
import requests
import pandas as pd

from app.main.utils import date_util

type_dict = {
    1: {"name": "顶级买单", "color": "red", "type": 'sl'},
    2: {"name": "顶级卖单", "color": "green", "type": 'sl'},
    4: {"name": "封涨停板", "color": "red", "type": 'price'},
    8: {"name": "封跌停板", "color": "green", "type": 'price'},
    16: {"name": "打开涨停板", "color": "green", "type": 'price'},
    32: {"name": "打开跌停板", "color": "red", "type": 'price'},
    64: {"name": "有大买盘", "color": "red", "type": 'sl'},
    128: {"name": "有大卖盘", "color": "green", "type": 'sl'},
    256: {"name": "机构买单", "color": "red", "type": 'sl'},
    512: {"name": "机构卖单", "color": "green", "type": 'sl'},
    8193: {"name": "大笔买入", "color": "red", "type": 'sl'},
    8194: {"name": "大笔卖出", "color": "green", "type": 'sl'},
    8195: {"name": "拖拉机买", "color": "red", "type": 'sl'},
    8196: {"name": "拖拉机卖", "color": "green", "type": 'sl'},
    8201: {"name": "火箭发射", "color": "red", "type": 'change'},
    8202: {"name": "快速反弹", "color": "red", "type": 'change'},
    8203: {"name": "高台跳水", "color": "green", "type": 'change'},
    8204: {"name": "加速下跌", "color": "green", "type": 'change'},
    8205: {"name": "买入撤单", "color": "green", "type": 'sl'},
    8206: {"name": "卖出撤单", "color": "red", "type": 'sl'},
    8207: {"name": "竞价上涨", "color": "red", "type": 'change'},
    8208: {"name": "竞价下跌", "color": "green", "type": 'change'},
    8209: {"name": "高开5日线", "color": "red", "type": 'change'},
    8210: {"name": "低开5日线", "color": "green", "type": 'change'},
    8211: {"name": "向上缺口", "color": "red", "type": 'change'},
    8212: {"name": "向下缺口", "color": "green", "type": 'change'},
    8213: {"name": "60日新高", "color": "red", "type": 'price'},
    8214: {"name": "60日新低", "color": "green", "type": 'price'},
    8215: {"name": "60日大幅上涨", "color": "red", "type": 'change'},
    8216: {"name": "60日大幅下跌", "color": "green", "type": 'change'},
    8217: {"name": "向上缺口", "color": "red", "type": 'change'},
    8218: {"name": "向下缺口", "color": "green", "type": 'change'}
}


def get_stock_changes(code, date, market):
    """
    MarketValue f116,市值
    PERation f162,市盈率(动),动态市盈率，总市值除以全年预估净利润，例如当前一季度净利润1000万，则预估全年净利润4000万
    staticPERation f163,静态市盈率,静态市盈率，总市值除以上一年度净利润
    RollingPERations f164,滚动市盈率 滚动市盈率，最新价除以最近4个季度的每股收益
    :param symbol:
    :return:
    """
    dt_str = date_util.dt_to_str(date)
    url = "http://push2ex.eastmoney.com/getStockChanges"
    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "code": code,
        "date": dt_str,
        "dpt": "wzchanges",
        "market": market
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    content = data_json["data"]
    if content is None: return content

    inner = content["data"]
    if len(inner) == 0: return None
    df = pd.DataFrame(inner)
    df.columns = [
        "time",
        "type",
        "price",  # 价格
        "detail",  # 买入,卖出笔数,or 涨跌幅度
        "up",  # 涨幅
        "volume",  # 成交量
        # 类型
        # 8194 大单卖出
    ]
    df['code'] = code
    df['date'] = date_util.get_start_of_day(date)
    print(dt_str)
    df['type_name'] = df.apply(lambda a: type_dict[a['type']]['name'],axis=1)

    return df


if __name__ == '__main__':
    changes = get_stock_changes("300821", "20210910")
    print(changes)
