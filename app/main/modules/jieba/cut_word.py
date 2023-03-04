import jieba
from app.main.utils import simple_util

rootPath = simple_util.get_root_path()
jieba.load_userdict(rootPath+"/app/static/finance_word.txt")

def cut(input)->list:
    """
    精确切割
    :param input:
    :return:
    """
    return list(jieba.cut(input,cut_all= False))

if __name__ == "__main__":
    r = cut("博时新能源汽车ETF")
    print(",".join(r))