# s = "S_1#机钒烧_TFe"
#
# path = "/Users/lifeng/Downloads/Oracle全.csv"
#
# import pandas as pd
# import re
#
# df = pd.read_csv(path,encoding="gbk")
#
# columns = list(df.columns)
#
# columns = [re.sub('^[A-Z]_', '', column) for column in columns[8:]]
# columns = ["["+column+"]" for column in columns[8:]]
#
# df2 = pd.read_excel("/Users/lifeng/Downloads/point.xls")
#
# df_in_need = df2[df2['data字段名'].isin( columns)].loc[:,['data字段名','字段名']]
# df_in_need.columns = ["name","field"]
#
#
#
# d = df_in_need.to_dict("records")
# fil = [ row["name"] for row in d]
#
# diff = [column for column in columns if column not in fil]
#
#
#
# print(123)
