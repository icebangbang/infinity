import backtrader as bt
import logging
from app.main.stock.company import CompanyGroup, Company
from app.main.stock.sub_startegy import SubST
from typing import List


class StrategyWrapper(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        logging.info('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, company: Company, sub_st: List[SubST], **kwargs):
        self.company = company
        company.init_ind(self.data)

    def next(self):
        self.company.next(self.data)


class SellStrategyWrapper(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        logging.info('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, company_group: CompanyGroup, sub_st: List[SubST], **kwargs):
        self.company_group = company_group

        for i, d in enumerate(self.datas):
            code = d._name
            logging.info("init {}".format(code))
            sub_st_instance = [st(**kwargs) for st in sub_st]
            company = Company(code,
                              *sub_st_instance
                              )
            company_group.add_company(company)

            company: Company = company_group.get_company(code)
            company.init_ind(d)

    def next(self):
        for i, d in enumerate(self.datas):
            code = d._name
            company: Company = self.company_group.get_company(code)
            company.next(d)
