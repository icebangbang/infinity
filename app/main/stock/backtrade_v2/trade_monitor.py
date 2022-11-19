"""
统计回测表现
"""
from app.main.stock.backtrade_v2.record import StockRefreshRecord
from app.main.stock.dao import k_line_dao
from app.main.utils import cal_util
from app.main.utils.date_util import WorkDayIterator
from typing import List
from datetime import datetime
import logging as log

class TradeMonitor:

    maximum_rollback = 0
    maximum_rollback_start = None
    maximum_rollback_end = None

    def cal_maximum_rollback(self, code,
                         refresh_record_list: List[StockRefreshRecord],
                         in_time: datetime,
                         current_time: datetime):
        """
        统计最大回撤
        :return:
        """

        refresh_record_dict = {refresh_record.date: refresh_record for refresh_record in refresh_record_list}
        k_line_data_list = k_line_dao.get_k_line_by_code([code], in_time, current_time)
        k_line_data_dict = {k_line_data['date']: k_line_data for k_line_data in k_line_data_list}

        for cursor in WorkDayIterator(in_time, current_time):
            for sub_cursor in WorkDayIterator(cursor, current_time):
                k_line_data = k_line_data_dict.get(current_time, None)
                refresh_record:StockRefreshRecord = refresh_record_dict[sub_cursor]

                close = k_line_data['close']
                cost = refresh_record.cost
                positions_num = refresh_record.positions_num

                rollback = cal_util.get_rate(close-cost,cost)
                if rollback < self.maximum_rollback:
                    self.maximum_rollback = rollback
                    self.maximum_rollback_start = sub_cursor
                    self.maximum_rollback_end = current_time

                log.info("{},{},{},最大回撤:{}".format(code,self.maximum_rollback_start,self.maximum_rollback_end,self.maximum_rollback))

