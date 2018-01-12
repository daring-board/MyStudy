import os
import sys
import numpy as np
import statistics as stats
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

def readClose(stock, flag=False):
    path = './data/Close/%s.csv'%stock
    if flag: path = './data/1592.csv'
    datas = [line.strip().split(',') for line in open(path, 'r', encoding='utf-8')][1:]
    dic = {row[1]: float(row[2]) for row in datas}
    return dic

def construct(s_info, date, c, noday):
    k = int(noday[:-1])
    for stock in c:
        s_info = StockInfo(stock, k)
        s_info.readDatas(noday)
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
    stocks = getStocks()
    noday = sys.argv[1]
#    noday = '5d'
    out_path = './result/pair_trade_%s.txt'%noday
    cd = CalcDist(noday)
    clust = cd.main()
    c_set = clust[noday]
    # whole = start = 100000
    whole = start = 1
    all_tax = 0
    with open(out_path, 'w') as f: f.write('■PairTrade Result\n')
    for c in c_set:
        s_infos = {}
        price = 0#whole / len(c_set)
        cl_price = 0
        tax = 0
        if len(c) < 4: continue
        with open(out_path, 'a') as f: f.write('Cluster: %s\n'%str(c))
        pred_dict = {}
        for stock in c:
            ret, date = readDatas(stock, noday)
            pred_dict[stock] = {date[idx]: float(ret[idx]) for idx in range(len(ret))}
        mean = 1#stats.mean(readClose('dummy', True).values())
        stock_dict = {stock: readClose(stock) for stock in c}
        stocks = {stock: 0 for stock in c}
        count = 0
        for d in date:
            s_info = construct(s_infos, d, c, noday)
            for stock in c:
                item = s_infos[stock].getVal()
                num = len(item[3])
                '''
                ペアトレードフラグが立っていない銘柄はスキップ
                '''
                if num == 0: continue
                '''
                トレンドが上昇ならば、買い
                '''
#                if item[1] == 1 and price - num * stock_dict[stock][d] > 0:
                if item[1] == 1:
                    #if d in stock_dict[stock].keys():
                    if False:
                        price -= num * stock_dict[stock][d]
                        tax +=  0.0002 * num * stock_dict[stock][d]
                    else:
                        price -= num * mean * pred_dict[stock][d]
                        tax +=  0.0002 * num * mean * pred_dict[stock][d]
                    stocks[stock] += num
#                if item[1] == -1 and stocks[stock] - num > 0:
                '''
                トレンドが下落ならば、売り
                '''
                if item[1] == -1:
#                    if d in stock_dict[stock].keys():
                    if False:
                        price += num * stock_dict[stock][d]
                        tax +=  0.0002 * num * stock_dict[stock][d]
                    else:
                        price += num * mean * pred_dict[stock][d]
                        tax +=  0.0002 * num * mean * pred_dict[stock][d]
                    stocks[stock] -= num
            '''
            損益を確定させる
            '''
            if count % int(noday[:-1]) == int(noday[:-1])-1:
                for stock in c:
#                    if d in stock_dict[stock].keys():
                    if False:
                        price += num * stock_dict[stock][d]
                    else:
                        price += num * mean * pred_dict[stock][d]
                    stocks[stock] = 0
                whole += price
                all_tax += tax
                cl_price += price
                with open(out_path, 'a') as f: f.write('%s: %.2f\n'%(d, price))
                print('%s: %.2f'%(d, price))
                price, tax = 0, 0
            count += 1
#            for stock in c: print('%s: %d'%(stock, stocks[stock]))
#            print('\n')
        with open(out_path, 'a') as f:
            f.write('Cluster_return: %.2f\n'%cl_price)
            f.write('G_return: %d\n'%whole)
        print(whole)
        cl_price = 0
    with open(out_path, 'a') as f:
        f.write('Gross: %.2f, 利益: %.2f, 利益率: %.2f\n'%(whole, whole-start, (whole-start)/start))
        f.write('Net: %.2f, 利益: %.2f, 利益率: %.2f\n'%(whole-all_tax, whole-all_tax-start, (whole-all_tax-start)/start))
    print('Gross: %.2f, 利益: %.2f, 利益率: %.2f'%(whole, whole-start, (whole-start)/start))
#    print('Net: %.2f, 利益: %.2f, 利益率: %.2f'%(whole-tax, whole-start-tax, (whole-start-tax)/start))
