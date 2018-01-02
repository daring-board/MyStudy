import os
import sys
import numpy as np
from calc_dist import CalcDist
from stock_info import StockInfo

class DynamicPrograming():

    def __init__(self, x, val, trend, date):
        self.x = int(x/2)
        self.v = val
        '''
        トレンドが下落ならば、1とする
        '''
        self.trend = {date: 1 if trend[date] < 0 else 0 for date in trend.keys()}
        self.DtoN = {date[idx]: idx for idx in range(len(date))}
        self.NtoD = date
        self.len = x
        self.act = {self.NtoD[idx]:{self.NtoD[idy]:[] for idy in range(idx+1, idx+self.len if len(date)>idx+self.len else len(date))} for idx in range(len(date))}
        self.opt = {self.NtoD[idx]:{self.NtoD[idy]: 0 for idy in range(idx+1, idx+self.len if len(date)>idx+self.len else len(date))} for idx in range(len(date))}

    '''
    :buy    : date(string)
    :sell   : date(string)
    '''
    def expectReturn(self, buy, sell):
        z = sum(self.trend[self.NtoD[idx]] for idx in range(self.DtoN[buy], self.DtoN[sell]+1))
        term1 = (self.x-self.DtoN[sell]-self.DtoN[buy]+1)
        term1 = 1 - term1 / (self.x-self.len-self.DtoN[buy]+1)
        term2 = 1 - z / (self.DtoN[sell]-self.DtoN[buy]+1)
        term3 = self.v[sell] - self.v[buy]
        return term1*term2*term3

    def commit(self, yesterday, today, alf):
        price = self.v
        if alf not in self.opt[yesterday]: return 0
        s_t = sum(price[today]-price[item[0]] if item[1] == today else 0 for item in self.act[yesterday][alf])
        return s_t

    def main(self):
        today = self.NtoD[0]
        for idy in range(self.DtoN[today]+1, self.DtoN[today]+self.len):
            alf = self.NtoD[idy]
            val = self.expectReturn(today, alf)
            if val > 0:
                self.opt[today][alf] = val
                self.act[today][alf].append((today, alf))
        for idx in range(1, len(self.NtoD)):
            today = self.NtoD[idx]
            yesterday = self.NtoD[idx-1]
            tmp, max_exp = [], 0
            length = self.DtoN[today]+self.len if len(self.NtoD) > self.DtoN[today]+self.len else len(self.NtoD)
            for idy in range(self.DtoN[today]+1, length):
                if self.NtoD[idy] not in self.opt[yesterday]: continue
                if max_exp < self.opt[yesterday][self.NtoD[idy]]:
                    max_exp = self.opt[yesterday][self.NtoD[idy]]
                    tmp = self.act[yesterday][self.NtoD[idy]]
            for idy in range(self.DtoN[today]+1, length):
                alf = self.NtoD[idy]
                if alf not in self.opt[yesterday]: continue
                val = max_exp + self.expectReturn(today, alf) + self.commit(yesterday, today, alf)
                self.act[today][alf] = tmp.copy()
                if val > self.opt[yesterday][alf]:
                    self.opt[today][alf] = val
                    self.act[today][alf].append((today, alf))
                else:
                    self.opt[today][alf] = self.opt[yesterday][alf] + self.commit(yesterday, today, alf)
        # with open('test.csv', 'w') as f:
        #     f.write('No,')
        #     for idx in range(1, self.len): f.write('%s,'%self.NtoD[idx])
        #     f.write('\n')
        #     for idx in range(0, self.len):
        #         f.write('%s,'%self.NtoD[idx])
        #         for idy in range(1, self.len):
        #             if self.NtoD[idy] not in self.opt[self.NtoD[idx]]: f.write('nan,')
        #             else: f.write('%f,'%self.opt[self.NtoD[idx]][self.NtoD[idy]])
        #         f.write('\n')

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
    for stock in stocks:
        print(stock)
        p_price, date = readDatas(stock, noday)
        p_price = {date[idx]: float(p_price[idx]) for idx in range(len(date))}
        trend, date = readTrend(stock, noday)
        trend = {date[idx]: float(trend[idx].strip()) for idx in range(len(date))}
        diff_trend = {date[idx]: trend[date[idx]]-trend[date[idx-1]] for idx in range(1, len(date))}
        dp = DynamicPrograming(int(noday[:-1]), p_price, trend, date)
        dp.main()
        act = dp.act[date[len(date)-2]][date[len(date)-1]]
        if len(act) == 0: continue
#        print(act)
        close = readClose(stock)
        count = 1
        with open('result/%s/%s_bs.csv'%(stock, noday), 'w') as f:
            f.write('No, buy, sell, unit, price\n')
            buy, sell, pre, num = act[0][0], act[0][1], act[0][1], 0
            price = 0
            for item in act:
                num += 1
                if pre == item[1] and item != act[-1]: continue
                if item[1] != 0:
                    if item == act[-1]: num += 1
                    if buy == act[0][0]: num -= 1
                    if sell in close.keys() and buy in close.keys():
                        f.write('%d,%s,%s,%d,%f\n'%(count, buy, sell, num ,num*(close[sell]-close[buy])))
                        price += num*(close[sell]-close[buy])
                    else:
                        f.write('%d,%s,%s,%d,%f*\n'%(count, buy, sell, num , num*(p_price[sell]-p_price[buy])))
                    count += 1
                    num = 0
                    pre = sell = item[1]
                    buy = item[0]
            f.write('%f\n'%price)
            f.write('No, buy, sell, price\n')
            count, price = 1, 0
            for item in act:
                if item[1] != 0:
                    buy, sell = item[0], item[1]
                    if sell in close.keys() and buy in close.keys():
                        f.write('%d,%s,%s,%d,%f\n'%(count, buy, sell, num ,close[sell]-close[buy]))
                        price += close[sell]-close[buy]
                    else:
                        f.write('%d,%s,%s,%d,%f*\n'%(count, buy, sell, num , p_price[sell]-p_price[buy]))
                    count += 1
            f.write('%f\n'%price)
            f.write(str(act)+'\n')
