from backtrader.feeds import PandasData
from app.main.stock.company import Company
from app.main.stock.sub_startegy import SubST


class VolumeSubST(SubST):
    """
        中短期上升策略
        """

    def __init__(self, **kwargs):
        """
        :param period: 布林轨道宽度
        :param match_num:
        """
        pass

    def init_ind(self, data: PandasData, company: Company):
        """
        初始化指标
        :return:
        """
        pass

    def next(self, data: PandasData, company: Company):

        print(data._name,str(data.datetime.date(0)),data.close[0])


        # day = data.buflen() - len(data)
        #
        #
        # if day != 0: return  # 只考虑当日触发情况
        #
        # company.set(constant.high_volume_10,data.volume[0] == pd.Series(data.volume.array[-10:]).max())
        # company.set(constant.high_volume_5,data.volume[0] == pd.Series(data.volume.array[-5:]).max())
