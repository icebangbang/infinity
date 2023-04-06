from datetime import datetime
from typing import Dict

from app.main.model import Basic


class BoardValue(Basic):
    value: Dict # 结果集
    date: datetime # 时间点
