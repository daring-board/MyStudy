import os
import sys
import numpy as np
import common_functions as cf
import random
from enum import Enum
from calc_dist import CalcDist
from stock_info import StockInfo

class ReinforcementLearning():
    ''' 強化学習を実行するクラス
    '''
    ACTIONS = Enum('Actions', 'sell stay buy commit')
    def __init__(self, prices, trends, w, dates):
        ''' コンストラクタ
        : prices: 予測株価
        : trends: トレンド
        : w: 総資産
        : dates: 学習期間
        '''
        self.prices = prices
        self.trends = trends
        self.w = w
        self.no = 0
        self.q = {d: {act: 0 for act in self.ACTIONS} for d in dates}
        self.pi = {d: 0 for d in dates}
        self.alf = 0.5 # 学習率
        self.gamma = 0.9 # 割引率
        self.dates = dates

    def setQ(self, q):
        self.q = q

    def getStatus(self, date):
        ''' 状態を取得する
        '''
        s = (date, self.prices[date], self.trends[date], self.w, self.no)
        return s

    def getAction(self, date, stat):
        ''' epsilon-greedy Algorithmで行動を選択する
        '''
        eps = 0.1
        whole = 100
        acts = [act for act in self.ACTIONS]
        if random.randint(0, whole) > eps*whole:
            max_q, act = 0, 0
            for a in self.q[date]:
                if max_q <= self.q[date][a]:
                    max_q = self.q[date][a]
                    act = a
        else:
            act = random.choice(acts)
        return act

    def getPayOff(self, date, act):
        ''' 報酬関数
        '''
        r = 0
        if act == self.ACTIONS.buy:
            r = -self.prices[date]
            self.no += 1
        elif act == self.ACTIONS.sell:
            r = self.prices[date]
            self.no -= 1
        elif act == self.ACTIONS.commit:
            r = self.no*self.prices[date]
            self.no = 0
        return {date: r}

    def updateQ(self, stat, act, r, now):
        ''' 行動価値関数を更新
        '''
        date = stat[0]
        max_q = 0
        for idx in range(1, 10):
            n_stat = self.getStatus(self.dates[now+idx])
            for a in self.q[n_stat[0]]:
                if max_q < self.q[n_stat[0]][a]:
                    max_q = self.q[n_stat[0]][a]
        self.q[date][act] = (1-self.alf)*self.q[date][act]
        self.q[date][act] += self.alf*(r[date]+self.gamma*max_q)

    def train(self, dates):
        for idx in range(len(dates)-10):
            d = dates[idx]
            stat = self.getStatus(d)
            act = self.getAction(d, stat)
            r = self.getPayOff(d, act)
            tmp = 99999
            while abs(tmp-self.q[d][act]) > 0.001:
                #print('%f: %f'%(tmp, self.q[d][act]))
                tmp = self.q[d][act]
                self.updateQ(stat, act, r, idx)

    def predict(self, dates, close):
        price = 0
        stock = 0
        # for idx in range(len(dates)):
        #     d = dates[idx]
        #     print('%s:%s'%(d,str(self.q[d])))
        for d in dates:
            stat = self.getStatus(d)
            act = self.getAction(d, stat)
#            print('%s: %s'%(d, act), end=':')
            if act == self.ACTIONS.buy:
                #price -= close[d]
                price -= self.prices[d]
                stock += 1
            elif act == self.ACTIONS.sell:
                #price += close[d]
                price += self.prices[d]
                stock -= 1
            elif act == self.ACTIONS.commit:
                #price += stock*close[d]
                price += stock*self.prices[d]
                stock = 0
#            print('%f, %d'%(price, stock))
        print('%f, %d'%(price, stock))
        return price

if __name__=='__main__':
    stocks = cf.getStocks()
    noday = sys.argv[1]
    for stock in stocks[:3]:
        print(stock)
        p_price, date = cf.readDatas(stock, noday)
        p_price = {date[idx]: float(p_price[idx]) for idx in range(len(date))}
        trend, date = cf.readTrend(stock, noday)
        trend = {date[idx]: float(trend[idx].strip()) for idx in range(len(date))}
        close = cf.readClose(stock)
#        print(close)
        dates = [item for item in date if item in close.keys()]
#        print(dates)
        rl = ReinforcementLearning(p_price, trend, 100000, dates)
        rl.train(dates)
        rl.predict(dates, close)
