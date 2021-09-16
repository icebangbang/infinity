from typing import Tuple, List, Dict
from app.main.stock.sub_startegy import SubST
from backtrader.feeds.pandafeed import PandasData
import logging
import json


class Company:

    def __init__(self, code, *st):
        self.match_time = []
        self.code = code
        self.sub_st_list: List[SubST] = list()
        self.sub_st_list.extend(st)

    def init_ind(self, data: PandasData):
        for sub_st in self.sub_st_list:
            sub_st.init_ind(data, self)

    def next(self, data: PandasData):
        for sub_st in self.sub_st_list:
            sub_st.next(data, self)

    def add_sub_st(self, *st: SubST):
        """
        添加子策略
        :return:
        """
        self.sub_st_list.extend(st)

    def get(self, name, default=None):
        try:
            obj = self.__getattribute__(name)
            if obj is None:
                return default
            return obj
        except AttributeError:
            return default


    def set(self, key, value):
        self.__setattr__(key, value)

    def set_condition(self,strategy,value):
        self.set(strategy.__class__.__name__,value)


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