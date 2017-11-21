import os
import numpy as np

class CalcDist():
    '''
    Calculate distance
    Stock i, j's predict stock price volatility graphs
    Use k-clustering
    '''
    def __init__(self):
        self.__k = 15
        self.__span = 60
        self.__input_path = './data/Close/'
#        self.__nd_list = ['5d', '10d', '15d', '20d']
        self.__nd_list = ['5d']

    def getStocks(self, dir_path):
        dir_list = os.listdir(dir_path)
        stocks = [item.split('.')[0] for item in dir_list]
        return stocks

    def readDatas(self, stock1, stock2, noday):
        path = './result/%s/result_%s.csv'%(stock1, noday)
        d1 = [line.split(',')[2] for line in open(path, 'r')][self.__span:]
        path = './result/%s/result_%s.csv'%(stock2, noday)
        d2 = [line.split(',')[2] for line in open(path, 'r')][self.__span:]
        dist = sum(abs(float(d1[idx])-float(d2[idx])) for idx in range(len(d1)))
        return dist

    def createDistMat(self, stocks, noday):
        d_mtx = {}
        for idx in range(len(stocks)-1):
            stock1 = stocks[idx]
            for idy in range(idx+1, len(stocks)):
                stock2 = stocks[idy]
                d_mtx[idx+idy*len(stocks)] = self.readDatas(stock1, stock2, noday)
        return d_mtx

    def createClusters(self, stocks, o_list):
        c_set = []
        count = 0
        while len(c_set) != self.__k:
            item = o_list[count]
            idx, idy = int(item[0]/len(stocks)), int(item[0]%len(stocks))
            tmp = set([stocks[idx], stocks[idy]])
            if len(c_set) == 0: c_set.append(tmp)
            else:
                flag = True
                for s in c_set:
                    if len(s.intersection(tmp)) != 0:
                        c_set.remove(s)
                        c_set.append(s.union(tmp))
                        flag = False
                        break
                if flag: c_set.append(tmp)
            count += 1
        print(c_set)

    def main(self):
        stocks = self.getStocks(self.__input_path)[:60]
        for noday in self.__nd_list:
            mtx = self.createDistMat(stocks, noday)
            ordered_list = sorted(mtx.items(), key=lambda x: x[1])
            self.createClusters(stocks, ordered_list)

if __name__=='__main__':
    cd = CalcDist()
    cd.main()
