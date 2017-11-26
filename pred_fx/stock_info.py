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
    k = 10
    th = 0.6
    def __init__(self, stock):
        self.__val = [0, 0, 0, None, 0]
        self.__stock = stock

    def readDatas(self):
        path = './result/%s/result_5d.csv'%self.__stock
        self.dats = pd.read_csv(path, index_col=None)

    def setDatas(self, date):
        idx = self.dats[self.dats['date'] == date].index[0]
        dat = self.dats[idx: idx+self.k+1]
        self.__val[0] = float(dat['predict'].values[0])
        self.setTrend(date)
        self.setEps(date)
        # self.setConf(date)
        print(self.__val)

    def getVal(self):
        return self.__val

    def setTrend(self, date):
        idx = self.dats[self.dats['date'] == date].index[0]
        trend = self.dats[idx: idx+self.k+1]
        diff = trend['trend'][1:] - trend.shift()['trend'][1:]
        u_count = sum(1 for row in diff if row > 0)
        d_count = sum(1 for row in diff if row < 0)
        print(u_count)
        print(d_count)
        self.__val[1] = 1 if u_count >= self.k*self.th else 0
        self.__val[1] = 1 if d_count >= self.k*self.th else 0

    def setEps(self, date):
        item = self.dats[self.dats['date'] == date]['confidence_interval'].values[0]
        val = item.split('_')[1].replace(')','')
        eps = float(val) - self.__val[0][0]
        self.__val[2] = eps

    def calcPairFlag(self, st):
        p1 = self.__val[0][0]
        p2 = st.getVal()[0]


    def setFlag(self, st):
        print('bb')

if __name__=='__main__':
    stocks = getStocks('./data/Close/')[:60]
    noday = '5d'
    cd = CalcDist()
    clust = cd.main()
    c_set = clust[noday]
    c = c_set.pop()
    s_infos = {}
    for stock in c:
        s_info = StockInfo(stock)
        s_info.readDatas()
        s_info.setDatas('2017/3/2')
        s_infos[stock] = s_info
    for stock1 in c:
        item1 = s_infos[stock1]
        for stock2 in c:
            if stock1==stock2: continue
            item2 = s_infos[stock2]
            item1.calcPairFlag(item2)
            item2.calcPairFlag(item1)
