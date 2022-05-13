"""
自定义方法
"""
from datetime import datetime, timedelta
import re
from typing import Dict

from app.main.utils import date_util
import inspect
import sys

def check_and_parse(request_body:Dict):
    new_dict = {}
    for key,value in request_body.items():
        if "#" in value:
            func_name = value.replace("#","")
            new_value = func_dict[func_name]()
            new_dict[key] = new_value

    request_body.update(new_dict)

    return request_body




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
    dt = date_util.get_work_day(base_time, offset)

    return dt

def current_date(**kwargs):
    return date_util.get_start_of_day(datetime.now())


func_dict = {}
for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isfunction(obj):
        func_dict[name] = obj

if __name__ == "__main__":
    check("#get_work_date($date,10)",{"date":"2022-02-10"})
