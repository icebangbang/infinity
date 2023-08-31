import akshare

if __name__ == "__main__":
    r = akshare.stock_dzjy_mrtj('20230203','20230203')

    for name, group in r.groupby("证券简称"):
        print(name,len(group))