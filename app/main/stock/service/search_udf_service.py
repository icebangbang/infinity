"""
自定义方法
"""
from datetime import datetime, timedelta
import re

from app.main.utils import date_util
import inspect
import sys


def check(expr,input):
    reg = r"#(.+?)\("
    param_reg = r"\((.+?)\)"

    if not isinstance(expr,str):
        return expr
    # #get_work_date($date,10)
    match_list = re.findall(reg, expr)
    if len(match_list) > 0:
        func_name =  match_list[0]
        match_param = re.findall(param_reg, expr)
        params = match_param[0].split(",")
        new_params = []
        for param in params:
            if "$" in param:
                param = input.get(param.replace("$",""))
            new_params.append(param)

        r = func_dict[func_name](*new_params)
        return r
    else:
        return expr


def get_work_date(base_time, offset):
    if isinstance(base_time,str):
        base_time = date_util.parse_date_time(base_time,"%Y-%m-%d")
    if isinstance(offset,str):
        offset = int(offset)
    dt, base_time = date_util.get_work_day(base_time, offset)

    return dt


func_dict = {}
for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isfunction(obj):
        func_dict[name] = obj

if __name__ == "__main__":
    check("#get_work_date(#date,10)",{"date":"2022-02-10"})
