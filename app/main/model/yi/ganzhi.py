from app.main.model import Basic


class GanZhi(Basic):
    gan: str
    zhi: str
    gan_index: int
    zhi_index: int

    def get_yuanyang_he(self):
        pass


class BaZi(Basic):
    """
    八字基本干支信息
    """
    year_gan: str  # 年干
    year_zhi: str  # 年支
    month_gan: str  # 月干
    month_zhi: str  # 月支
    day_gan: str  # 日干
    day_zhi: str  # 日支
    hour_gan: str  # 时干
    hour_zhi: str  # 时支
    year_gan_index: int  # 数字索引
    year_zhi_index: int  # 数字索引
    month_gan_index: int  # 数字索引
    month_zhi_index: int  # 数字索引
    day_gan_index: int  # 数字索引
    day_zhi_index: int  # 数字索引
    hour_gan_index: int  # 数字索引
    hour_zhi_index: int  # 数字索引

    year_gz: GanZhi
    month_gz: GanZhi
    day_gz: GanZhi
    hour_gz: GanZhi

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year_gz = GanZhi(gan=self.year_gan, zhi=self.year_zhi, gan_index=self.year_gan_index,
                              zhi_index=self.year_zhi_index)
        self.month_gz = GanZhi(gan=self.month_gan, zhi=self.month_zhi, gan_index=self.month_gan_index,
                               zhi_index=self.month_zhi_index)
        self.day_gz = GanZhi(gan=self.day_gan, zhi=self.day_zhi, gan_index=self.day_gan_index,
                             zhi_index=self.day_zhi_index)
        self.hour_gz = GanZhi(gan=self.hour_gan, zhi=self.hour_zhi, gan_index=self.hour_gan_index,
                              zhi_index=self.hour_zhi_index)

    def __str__(self):
        return "{}{}-{}{}-{}{}-{}{}".format(self.year_gan, self.year_zhi,
                                            self.month_gan, self.month_zhi,
                                            self.day_gan, self.day_zhi,
                                            self.hour_gan, self.hour_zhi)

    def get_yuanyang_he(self):
        """
        获得匹配的天地鸳鸯和
        :return:
        """
