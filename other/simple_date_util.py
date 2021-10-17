from app.main.utils import date_util


def get_repayment_time(current_repayment_time, update_time):
    day = date_util.get_days_between(update_time, current_repayment_time)
    if day > 0: return update_time

    return current_repayment_time


def get_new_repayment_time(time, day):
    return date_util.day_incr(time, day)
