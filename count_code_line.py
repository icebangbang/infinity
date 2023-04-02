import os
import time
from datetime import datetime

import pandas as pd

from app.main.utils import date_util, collection_util

filelists = []
# 指定想要统计的文件类型
whitelist = ['php', 'py']


# 遍历文件, 递归遍历文件夹中的所有
def getFile(basedir):
    global filelists
    for parent, dirnames, filenames in os.walk(basedir):
        # for dirname in dirnames:
        #    getFile(os.path.join(parent,dirname)) #递归
        for filename in filenames:
            ext = filename.split('.')[-1]
            # 只统计指定的文件类型，略过一些log和cache文件
            if ext in whitelist:
                filelists.append(os.path.join(parent, filename))


# 统计一个文件的行数
def countLine(fname):
    tatal_count = 0
    empty_row = 0
    comment_row = 0
    for file_line in open(fname).readlines():
        if file_line == '' or file_line == '\n':  # 过滤掉空行
            empty_row += 1
        if "#" in file_line:
            comment_row += 1
        tatal_count += 1
    print(fname + '----', tatal_count)
    return tatal_count, comment_row, empty_row


def do_sum(basedir):
    getFile(basedir)
    total = 0
    comment = 0
    empty = 0
    for filelist in filelists:
        tatal_count, comment_row, empty_row = countLine(filelist)
        total = total + tatal_count
        comment = comment + comment_row
        empty = empty + empty_row
    return total, comment, empty


if __name__ == '__main__':
    startTime = time.perf_counter()
    root_dir = '/home/lifeng/WORK/code'
    infinity = root_dir + '/python/infinity/'
    dest_statistic = infinity + "/app/static/code_statistic.csv"
    total, comment, empty = do_sum(infinity)

    df = pd.read_csv(dest_statistic,dtype={'project': str})

    rows = df.to_dict(orient="records")

    current_row = dict(project='infinity',
                       date=date_util.dt_to_str(datetime.now()),
                       total=total, comment=comment,
                       empty=empty)

    if collection_util.is_not_empty(rows) and str(rows[-1]['date'])==current_row['date']:
        rows[-1] = current_row
    else:
        rows.append(current_row)
    df = pd.DataFrame(rows)
    df.to_csv(dest_statistic, index=False, encoding='utf-8')

    print('lines:', total, comment, empty)
    print('Done! Cost Time: %0.2f second' % (time.perf_counter() - startTime))
