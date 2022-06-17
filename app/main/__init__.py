

def parse(condition_str):
    start = condition_str[0:1]
    condition_str = condition_str[1:]
    end = condition_str[-1]
    condition_str = condition_str[:-1]
    f1 = condition_str.split(",")[0]
    f2 = condition_str.split(",")[1]

    return start, end, f1, f2

def run():
    from interval3 import Interval
    import pandas as pd
    import pickle

    df = pd.read_excel("/Users/lifeng/Downloads/含钒-最佳值和操作范围0613.xls")

    rule_set = {}
    columns = list(df.columns)
    for index, row in df.iterrows():
        start, end, f1, f2 = parse(row["V2O5"])
        i = Interval(lower_bound=float(f1), upper_bound=float(f2),
                     lower_closed=start == "[",
                     upper_closed=end == "]")
        for column in columns:
            if column.startswith("CG"):
                print(column)
                inner_rule = rule_set.get(column, {})

                start, end, f1, f2 = parse(row[column])
                m = Interval(lower_bound=float(f1), upper_bound=float(f2),
                             lower_closed=start == "[",
                             upper_closed=end == "]")

                inner_rule[i] = m
                rule_set[column] = inner_rule
                pass

    a = rule_set
    interval = rule_set['CG_LT_GL_GL04_CO2ZXFX'][list(rule_set['CG_LT_GL_GL04_CO2ZXFX'].keys())[0]]
    interval > Interval(upper_bound=3)
# pickle.dump(rule_set, open("./dist_dict.pk", "wb"))
