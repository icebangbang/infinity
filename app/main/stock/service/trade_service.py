"""
交易节点相关实现
"""
def holder_query(**kwargs)->str:
    holder_id = kwargs['holderId']
    if (holder_id % 2==0):
        return "没有持仓"
    return "已有持仓"

