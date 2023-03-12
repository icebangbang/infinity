from typing import List, Dict

from app.main.model import Basic


class YAxisDesc(Basic):
    """
    y轴的描述信息
    """
    name: str  # y轴的名称
    scale: bool
    position: str  # 位置信息
    max: float  # y轴的最大值
    min: float  # y轴的最小值


class YAxisData(Basic):
    """
    y轴的具体数据
    """
    name: str  # 数据集名称
    y: List[float]  # 数值列表
    yAxisIndex: int  # 对应的YAxisDesc对象在整个列表的index位置
    markArea:any
    color:str
    markLine:dict



class Legend(Basic):
    """
    echart 图例组件的配置
    """
    # 要展示的图例
    data: List[str]
    # 被选中的图例
    selected: Dict
