from datetime import datetime, timedelta, timezone


def change_timezone():
    """

    :return: 返回中国时区时间
    """
    utc_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    # 8为中国时区
    cn_time = utc_time.astimezone(timezone(timedelta(hours=8)))
    return cn_time.strftime('%Y-%m-%d %H:%M:%S')