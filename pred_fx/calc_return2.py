import os
import sys
import numpy as np
from calc_dist import CalcDist

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

def calMean(v_list):
    mean = sum(v_list)/len(v_list)
    return mean

def calSTD(v_list):
    vals = np.array(v_list)
    return np.std(vals)

if __name__=='__main__':
    noday = '5d'
    stocks = getStocks()[:60]
    cd = CalcDist()
    clust = cd.main()
    #for key in clust.keys():
    c_set = clust[noday]
    datas = {}
    buy_sell = {}
    date = []
    for c in c_set:
        whole = 0
        if len(c) == 1: continue
        for stock in c: datas[stock], date = readDatas(stock, noday)
        means = []
        stds = []
        for idx in range(len(datas[c[0]])):
            v_list = [float(datas[stock][idx]) for stock in c]
            means.append(calMean(v_list))
            stds.append(2*calSTD(v_list)/3)
        for stock in c:
            tmp = []
            for idx in range(len(datas[c[0]])):
                # 割安 ならば、買いフラグ
                item  = 1 if means[idx]-stds[idx] < float(datas[stock][idx]) else 0
                if item == 0:
                    # 割高 ならば、売りフラグ
                    item  = -1 if means[idx]+stds[idx] > float(datas[stock][idx]) else 0
                tmp.append(item)
                #print('%f (%f, %f) %d'%(float(datas[stock][idx]), means[idx]-stds[idx], means[idx]+stds[idx], item))
            buy_sell[stock] = tmp
        price = 0
        stock_dict = {stock: readClose(stock) for stock in c}
        stock_num = {stock: 0 for stock in c}
        print(c)
        for idx in range(len(datas[c[0]])):
            for stock in c:
                c_dict = stock_dict[stock]
                # 買いフラグの場合
                if buy_sell[stock][idx] == 1:
                    price -= c_dict[date[idx]]
                    stock_num[stock] += 1
                # 売りフラグの場合
                if buy_sell[stock][idx] == -1 and stock_num[stock] > 1:
                    price += c_dict[date[idx]]
                    stock_num[stock] -= 1
            if idx == len(datas[c[0]]) - 1:
                for stock in c: price += c_dict[date[idx]]*stock_num[stock]
            print('%s: %.2f'%(date[idx], price))
            for stock in c: print('%s: %d'%(stock, stock_num[stock]))
#            input('Press enter to continue: ')
        whole += price
        print('all:{}'.format(whole))
