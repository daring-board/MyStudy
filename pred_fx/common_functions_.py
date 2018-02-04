import os
import sys
import numpy as np

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
