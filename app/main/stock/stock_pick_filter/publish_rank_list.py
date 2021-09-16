from datetime import datetime, timedelta
import pandas as pd

from app.main.stock.dao import k_line_dao, stock_dao
from app.main.stock.service import stock_service
from app.main.utils import date_util

import logging

stock_service.publish(2, 30)
