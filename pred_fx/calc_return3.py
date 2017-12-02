import os
import sys
import numpy as np
from calc_dist import CalcDist
from stock_info import StockInfo

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

def readClose(stock):
    path = './data/Close/%s.csv'%stock
    datas = [line.strip().split(',') for line in open(path, 'r', encoding='utf-8')][1:]
    dic = {row[0]: float(row[1]) for row in datas}
    return dic

def construct(s_info, date, c):
    for stock in c:
        s_info = StockInfo(stock)
        s_info.readDatas()
        s_info.setDatas(d)
        s_infos[stock] = s_info
    for idx in range(len(list(c))):
        stock1 = list(c)[idx]
        item1 = s_infos[stock1]
        for stock2 in list(c)[idx+1:]:
            item2 = s_infos[stock2]
            item1.calcPairFlag(item2)
            item2.calcPairFlag(item1)
    return s_info

if __name__=='__main__':
    stocks = getStocks()[:60]
    noday = '5d'
    cd = CalcDist()
    clust = cd.main()
    c_set = clust[noday]
    whole = start = 100000
    tax = 0
    for c in c_set:
        s_infos = {}
        commit, savings = 0, 0
        if len(c) < 4: continue
        for stock in c: ret, date = readDatas(stock, noday)
        stock_dict = {stock: readClose(stock) for stock in c}
        stocks = {stock: 0 for stock in c}
        count = 1
        for d in date:
            s_info = construct(s_infos, d, c)
            for stock in c:
                item = s_infos[stock].getVal()
                num = len(item[3])
                if num == 0: continue
                # 買い
                if item[1] == 1:
                    savings -= num * stock_dict[stock][d]
                    stocks[stock] += num
                    tax +=  0.02 * num * stock_dict[stock][d]
                # 売り
                if item[1] == -1:
                    commit += num * stock_dict[stock][d]
                    stocks[stock] -= num
                    tax +=  0.02 * num * stock_dict[stock][d]
            if count % int(noday[:-1]) == 0:
                for stock in c:
                    commit += stocks[stock] * stock_dict[stock][d]
                    stocks[stock] = 0
            count += 1
#            if count % int(noday[:-1]) == 0: print('%s: %.2f'%(d, savings + commit))
#            for stock in c: print('%s: %d'%(stock, stocks[stock]))
#            print('\n')
        whole += savings + commit
        print(whole)
    print('Gross: %.2f, 利益: %.2f, 利益率: %.2f'%(whole, whole-start, (whole-start)/start))
#    print('Net: %.2f, 利益: %.2f, 利益率: %.2f'%(whole-tax, whole-start-tax, (whole-start-tax)/start))
