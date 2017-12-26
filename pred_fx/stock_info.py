import os
import pandas as pd
import numpy as np
from calc_dist import CalcDist

def getStocks(dir_path):
    dir_list = os.listdir(dir_path)
    stocks = [item.split('.')[0] for item in dir_list]
    return stocks

class StockInfo():
    '''
    class StockInfo
    (v, u, eps, p, f)
    v: Predicted Stock Price
    u: Trend Value
    eps: Confidence Interval Parameter
    f: flag of Pair trade
    p: Rate Confidence
    '''
    alf = 0.8
    th = 0.8
    def __init__(self, stock, k):
        self.__val = [0, 0, 0, [], 0]
        self.__stock = stock
        self.k = k

    def readDatas(self, noday):
        path = './result/%s/result_%s.csv'%(self.__stock, noday)
        self.dats = pd.read_csv(path, index_col=None)

    def setDatas(self, date):
        self.__date = date
        idx = self.dats[self.dats['date'] == date].index[0]
        dat = self.dats[idx: idx+self.k+1]
        self.__val[0] = float(dat['predict'].values[0])
        self.setTrend(date)
        self.setEps(date)
        # self.setConf(date)
#        print(self.__val)

    def getVal(self):
        return self.__val

    def getStockNum(self):
        return self.__stock

    def setTrend(self, date):
        idx = self.dats[self.dats['date'] == date].index[0]
        trend = self.dats[idx: idx+self.k+1]
        diff = trend['trend'][1:] - trend.shift()['trend'][1:]
        u_count = sum(1 for row in diff if row > 0)
        d_count = sum(1 for row in diff if row < 0)
        self.__val[1] = 1 if u_count >= self.k*self.th else 0
        self.__val[1] = -1 if d_count >= self.k*self.th else self.__val[1]

    def setEps(self, date):
        item = self.dats[self.dats['date'] == date]['confidence_interval'].values[0]
        val = item.split('_')[1].replace(')','')
        eps = float(val) - self.__val[0]
        self.__val[2] = self.alf * eps

    def calcPairFlag(self, st):
        t1 = self.__val[1]
        t2 = st.getVal()[1]
        if t1 == t2 or t1 == 0 or t2 == 0: return
        date = self.__date
        idx = self.dats[self.dats['date'] == date].index[0]
        dat = self.dats[idx: idx+self.k+1]
        count = 0
        for date in dat['date']:
            p1_k = float(self.dats[self.dats['date'] == date]['predict'].values[0])
            p2_k = float(st.dats[st.dats['date'] == date]['predict'].values[0])
            cond1_k = True if abs(p1_k-p2_k) < self.__val[2] else False
            cond2_k = True if abs(p1_k-p2_k) < st.getVal()[2] else False
            if cond1_k and cond2_k:
                self.__val[3].append((self.__date, count, st.getStockNum()))
            count += 1


if __name__=='__main__':
    stocks = getStocks('./data/Close/')[:60]
    noday = '5d'
    cd = CalcDist()
    clust = cd.main()
    c_set = clust[noday]
    for c in c_set:
        if len(c) < 2: continue
        print(c)
        s_infos = {}
        for stock in c:
            s_info = StockInfo(stock)
            s_info.readDatas()
            s_info.setDatas('2017/3/2')
            s_infos[stock] = s_info
        for idx in range(len(list(c))):
            stock1 = list(c)[idx]
            item1 = s_infos[stock1]
            for stock2 in list(c)[idx+1:]:
                item2 = s_infos[stock2]
                item1.calcPairFlag(item2)
                item2.calcPairFlag(item1)
        for stock in c: print('%s, %s'%(stock, str(s_infos[stock].getVal())))
