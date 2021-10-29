from typing import Tuple, List, Dict
from app.main.stock.sub_startegy import SubST
from backtrader.feeds.pandafeed import PandasData
import logging
import json


class Company:

    def __init__(self, code, name,*st):
        self.match_time = []
        self.code = code
        self.name = name
        self.sub_st_list: List[SubST] = list()
        self.sub_st_list.extend(st)
        self.inds = {}
        self.features = {}

    def init_ind(self, datas: List[PandasData]):
        for sub_st in self.sub_st_list:
            sub_st.init_ind(datas, self)

    def next(self, datas: List[PandasData]):
        for sub_st in self.sub_st_list:
            sub_st.next(datas, self)

    def add_sub_st(self, *st: SubST):
        """
        添加子策略
        :return:
        """
        self.sub_st_list.extend(st)

    def get(self, name, default=None):
        if name in self.features.keys():
            return self.features[name]
        else:
            return default

    def set(self, key, value):
        self.features[key] = value

    def setInd(self, key, value):
        self.inds[key] = value

    def getInd(self, key):
        return self.inds[key]

    def set_condition(self, strategy, value):
        self.set(strategy.__class__.__name__, value)

    def macth_condition(self) -> bool:
        logging.info(self.code)
        result = [st.match_condition(self) for st in self.sub_st_list]
        logging.info(json.dumps(result))
        return all(result)

    def __str__(self):
        return self.code


class CompanyGroup:
    items: Dict[str, Company] = dict()

    def add_company(self, company: Company):
        code = company.code
        self.items[code] = company

    def get_company(self, code):
        return self.items.get(code)

    def get_matched_company(self):
        return [company for company in self.items.values() if company.macth_condition()]

    def get_companies(self):
        return list(self.items.values())
