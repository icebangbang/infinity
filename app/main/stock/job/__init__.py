# import numpy as np
# from scipy import linalg
# import matplotlib.pyplot as plt
# import pandas as pd
#
# X = np.array([1,2,3,4,7])
# Y = np.array([22,33,44,55,66])
#
# X0 = []
# data = pd.DataFrame()
# for i in range(len(X)):
#     X0.append([1,X[i]])
# r = linalg.lstsq(np.array(X0) , np.array(Y))
# print('回归直线斜率为：',r[0][1])
# print('回归直线纵截距为：',r[0][0])
# data['X']=X
# data['Y']=Y
# print(data.corr())
#
# X1 =np.arange(0.9*min(X),1.1*max(X),0.1)
#
# plt.figure(figsize=(10.24,7.68))
# plt.grid(zorder=0)
#
# p1 = plt.scatter(X , Y , marker = '+',s=150,color = 'black',zorder=3)
# p2 = plt.plot(X1,r[0][0]+r[0][1]*np.array(X1),color = 'blue',linewidth=2,label="$Y = {} X + {}$".format(float(str(r[0][1])[:6]),float(str(r[0][0])[:6])),zorder=2)
# plt.legend(fontsize=20,loc='upper left')
#
# plt.xlim(0.9*min(X),1.1*max(X))
# plt.ylim(0.9*min(Y),1.1*max(Y))
# plt.xticks(fontsize=20)
# plt.yticks(fontsize=20)
# plt.xlabel('$X$',fontsize=25)
# plt.ylabel('$Y$',fontsize=25)
# plt.show()

if __name__ == "__main__":
    import time
    from datetime import datetime
    t = time.strptime("93012",'%H%M%S')
    t2 =datetime(2021,9,10,t.tm_hour,t.tm_min,t.tm_sec)
    print(t2)
