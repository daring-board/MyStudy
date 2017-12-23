import os
import numpy as np

class CalcDist():
    '''
    Calculate distance
    Stock i, j's predict stock price volatility graphs
    Use k-clustering
    '''
    def __init__(self, noday):
        self.__k = 70
        self.__span = 60
        self.__input_path = './data/Close/'
        self.__noday = noday

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

    def Find(self, u):
        ''' return Name of set contains vertex u
        '''
        return self.__comp[u]

    def Union(self, A, B):
        ''' return new Set of Union A and B
        '''
        S = A.union(B)
        for item in S: self.__comp[item] = S

    def MakeUnionFind(self, S):
        self.__comp = {item: set([item]) for item in S}

    def clustersSize(self):
        clusters = set()
        for val in self.__comp.values():
            clusters.add(tuple(val))
        return len(clusters)

    def createClusters(self, stocks, o_list):
        self.MakeUnionFind(stocks)
        count = 0
        while self.__k < self.clustersSize():
            item = o_list[count]
            idx, idy = int(item[0]/len(stocks)), int(item[0]%len(stocks))
            s1 = set([stocks[idx]])
            s2 = set([stocks[idy]])
            if count == 0: self.Union(s1, s2)
            elif self.Find(stocks[idx]) != self.Find(stocks[idy]):
                self.Union(self.Find(stocks[idx]), self.Find(stocks[idy]))
            count += 1
        clusters = set()
        for val in self.__comp.values():
            clusters.add(tuple(val))
        return clusters

    def main(self):
        stocks = self.getStocks(self.__input_path)
        clust = {}
        noday = self.__noday
        mtx = self.createDistMat(stocks, noday)
        ordered_list = sorted(mtx.items(), key=lambda x: x[1])
        clusters = self.createClusters(stocks, ordered_list)
        clust[noday] = clusters
        return clust

if __name__=='__main__':
    cd = CalcDist()
    cd.main()
