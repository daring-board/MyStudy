import os
import sys
import numpy as np
from calc_dist import CalcDist
from stock_info import StockInfo

class DynamicPrograming():

    def __init__(self, x, val, trend, date):
        print('construct')
        self.x = x
        self.v = val
        '''
        トレンドが下落ならば、1とする
        '''
        self.trend = {date: 1 if trend[date] < 0 else 0 for date in trend.keys()}
        self.DtoN = {date[idx]: idx for idx in range(len(date))}
        self.NtoD = date
        self.len = len(date)

    '''
    :buy    : date(string)
    :sell   : date(string)
    '''
    def expectReturn(self, buy, sell):
        print('expectReturn')
        z = sum(self.trend[self.NtoD[idx]] for idx in range(self.DtoN[buy], self.DtoN[sell]+1))
        term1 = (self.x-self.DtoN[sell]-self.DtoN[buy]+1)
        term1 = 1 - term1 / (self.x-self.len-self.DtoN[buy]+1)
        term2 = 1 - z / (self.DtoN[sell]-self.DtoN[buy]+1)
        term3 = self.v[sell] - self.v[buy]
        print('%f*%f*%f=%f\n'%(term1, term2, term3, term1*term2*term3))
        return term1*term2*term3

    def commit(self):
        print('commit')

def getStocks():
    input_path = './data/Close/'
    dir_list = os.listdir(input_path)
    stocks = [item.split('.')[0] for item in dir_list]
    return stocks

def readDatas(stock, noday):
    path = './result/%s/result_%s.csv'%(stock, noday)
    d = [line.split(',')[2] for line in open(path, 'r')][-60:]
    date = [line.split(',')[0] for line in open(path, 'r')][-60:]
    return d, date

def readTrend(stock, noday):
    path = './result/%s/result_%s.csv'%(stock, noday)
    d = [line.split(',')[5] for line in open(path, 'r')][-60:]
    date = [line.split(',')[0] for line in open(path, 'r')][-60:]
    return d, date

def readClose(stock):
    path = './data/Close/%s.csv'%stock
    datas = [line.strip().split(',') for line in open(path, 'r', encoding='utf-8')][1:]
    dic = {row[1]: float(row[2]) for row in datas}
    return dic

if __name__=='__main__':
    stocks = getStocks()
    noday = sys.argv[1]
    stock = stocks[0]
    p_price, date = readDatas(stock, noday)
    p_price = {date[idx]: float(p_price[idx]) for idx in range(len(date))}
    trend, date = readTrend(stock, noday)
    trend = {date[idx]: float(trend[idx].strip()) for idx in range(len(date))}
    diff_trend = {date[idx]: trend[date[idx]]-trend[date[idx-1]] for idx in range(1, len(date))}
    print(diff_trend)
    dp = DynamicPrograming(5, p_price, trend, date)
    e_ta = dp.expectReturn('2017-09-27', '2017-10-17')
    print(e_ta)
