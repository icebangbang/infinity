def market_belong(code:str):
    """
    判断是深市,创业板,沪市,科创
    :return:
    """
    if code.startswith("30"): return "创业板"
    if code.startswith("60"): return "沪市"
    if code.startswith("00"): return "深市"
    if code.startswith("68"): return "科创板"

    return "err"

def basic_belong(code:str):
    """
    判断是深市,沪市
    :return:
    """
    if code.startswith("30"): return "SZ"
    if code.startswith("60"): return "SH"
    if code.startswith("00"): return "SZ"
    if code.startswith("68"): return "SH"

    return "err"
