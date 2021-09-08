import backtrader as bt
import logging
from app.main.stock.company import CompanyGroup, Company
from app.main.stock.sub_startegy.up_sma import UpSma
from app.main.stock.sub_startegy.down_bolling import DownBolling
from app.main.stock.sub_startegy.kdj_golden import KdjGolden
from app.main.stock.sub_startegy.heavy_vol import HeavyVol
from app.main.stock.sub_startegy.bolling_width import BollingWidth


class StrategyWrapper(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        logging.info('%s, %s' % (dt.isoformat(), txt))

    def __init__(self, company_group: CompanyGroup):
        self.company_group = company_group

        for i, d in enumerate(self.datas):
            code = d._name
            logging.info("init {}".format(code))
            company = Company(code,
                              HeavyVol(),
                              KdjGolden(),
                              BollingWidth()
                              )
            company_group.add_company(company)

            company: Company = company_group.get_company(code)
            company.init_ind(d)

    def next(self):
        for i, d in enumerate(self.datas):
            code = d._name
            company: Company = self.company_group.get_company(code)
            company.next(d)
