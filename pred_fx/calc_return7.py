# Dyna-Q
import os
import sys
import random
import pickle
import numpy as np
from scipy import signal
import common_functions as common
random.seed(1)

'''
Action: a in {buy: 1, hold: 0, commit: -1}
State : (risk, stock) risk, stock in INT: risk = p_stdev, stock = number of stock
Reward: commit_value[date] + price[date] * stock[date]
'''
class ReinforcementLearning:
    ''' Constructor'''
    def __init__(self, train_data, test_data):
        self._close = train_data
        self._pred = test_data
        self._p = {date: 0 for date in (list(self._close.keys())+list(self._pred.keys()))}
        self._alp = 0.1         # Learning rate
        self._gam = 0.8         # Discount rate
        self._span = 20         # Spans for standerd devision
        self._div = 0.5         # State divide 状態の分割単位：標準偏差の0.5倍分割
        self._tax = 0.002       # 手数料0.002%
        self._f = 0.9           # 投資比率
        self._init = 100000     # 初期投資
        ''' Init'''
        self._actions = [-1, 0, 1, 3, 5]
        self._states = {0: (0, 0, 0)}
        self._q = {0: {act: 0 for act in self._actions}}       # Q-Table
        self._model = {0: {act: {'reward': 0, 'state': 0} for act in self._actions}}

    def _eps_greedy(self, state_id, date, counter=1000):
        counter = 1000 if counter > 1000 else counter
        date_list = list(self._close.keys())+list(self._pred.keys())
        pos_today = self._get_start_pos(date_list, date)
        yesterday = date_list[pos_today-1]
        state = self._states[state_id]
        action = random.choice(self._actions)
        if random.random() > 1 / counter:
            action = max(self._q[state_id], key=self._q[state_id].get)
        # 保有証券数が上限であるか？
        if action >= 1 and state[1] >= 10:
            action = random.choice(self._actions[:2])
        # 空売りは行わない
        if action == -1 and state[1] == 0:
            action = 0
        return action

    def _get_start_pos(self, date_list, date):
        for idx in range(len(date_list)):
            if date_list[idx] == date:
                pos = idx
                break
        return pos

    def _calc_stats(self, date):
        prices = {}
        prices.update(self._close)
        prices.update(self._pred)
        date_list = list(self._close.keys())+list(self._pred.keys())
        pos_today = self._get_start_pos(date_list, date)
        prev_20 = np.array([prices[d] for d in date_list[pos_today-self._span: pos_today-1]])
        mean = np.mean(prev_20)
        std = np.std(prev_20)
        trend = prev_20 - signal.detrend(prev_20)
        trend_flag = int((np.diff(trend)[0]/10))
        return std, mean, trend_flag

    def _calc_risk(self, date_list, pos_today, mean, std, mode='train'):
        prices = self._close if mode == 'train' else self._pred
        return int(abs(prices[date_list[pos_today-1]] - mean) / (self._div * std))

    def _exprimental(self, date, state_id, action):
        date_list = list(self._close.keys())+list(self._pred.keys())
        pos_today = self._get_start_pos(date_list, date)
        p_t = self._p[date]
        stock = self._states[state_id][1]
        std, mean, trend = self._calc_stats(date)
        risk = self._calc_risk(date_list, pos_today, mean, std)
        risk = 1 if risk == 0 else risk
        if action == 0:
            ''' hold'''
            p_t1 = p_t + (stock * self._close[date]) / risk
        elif action >= 1:
            ''' buy'''
            stock += action
            p_t1 = (p_t - action * self._close[date]) + ((stock - self._tax) * self._close[date]) / risk
        elif action == -1:
            ''' commit'''
            p_t1 = p_t + (stock - self._tax) * self._close[date]
            stock = 0
        self._p[date_list[pos_today+1]] = p_t1
        reward = p_t1 / p_t - 1 if p_t != 0 else 0
        next_state = (risk, stock, trend)
        idx = len(self._states)
        if next_state not in self._states.values():
            self._states[idx] = next_state
        else:
            for i, s in self._states.items():
                if s == next_state: idx = i
        return reward, idx

    def _is_exist_state(self, state_id):
        if state_id in self._q: return
        self._q[state_id] = {act: 0 for act in self._actions}
        self._model[state_id] = {act: {'reward': 0, 'state': 0} for act in self._actions}

    def training(self, num):
        for i in range(1, num+1):
            current = 0 # current state id
            self._p = {date: 0 for date in (list(self._close.keys())+list(self._pred.keys()))}
            self._p[list(self._close.keys())[self._span]] = self._init
            ''' Episorde start '''
            for date in list(self._close.keys())[self._span:]:
                action = self._eps_greedy(current, date, i)
                reward, next_state = self._exprimental(date, current, action)
                self._is_exist_state(next_state)
                ''' Direct ReinforcementLearning '''
                max_q = max(self._q[next_state].values())
                self._q[current][action] += self._alp*(np.log(1+reward*self._f)+self._gam*max_q-self._q[current][action])
                ''' Update Model '''
                self._model[current][action] = {'reward': reward, 'state': next_state}
                current = next_state
            print('episorde: %d, Q-table size: %d'%(i, len(self._q)))
        with open('q_table.txt', 'w') as f:
            for key in self._q.keys(): f.write('%d %s: %s\n'%(key, str(self._states[key]), str(self._q[key])))

    def predict(self):
        train_list = list(self._close.keys())
        date_list = list(self._pred.keys())
        profit = np.array([self._init for idx in range(self._span+1)])
        stock = 0
        self._p = {date: 0 for date in (train_list+date_list)}
        self._p[date_list[0]] = self._init
        f = open('profit.txt', 'w')
        ''' Episorde start '''
        for date in date_list:
            std, mean, trend = self._calc_stats(date)
            pos_today = self._get_start_pos(date_list, date)
            risk = self._calc_risk(date_list, pos_today, mean, std, 'pred')
            next_state = (risk, stock, trend)
            state_id = 0
            # リスクの値のみ一致する状態
            for i, s in self._states.items():
                if s[0] == next_state[0]: state_id = i
            # 一致する状態
            for i, s in self._states.items():
                if s == next_state: state_id = i
            action = 0
            if state_id in self._q:
                action = max(self._q[state_id], key=self._q[state_id].get)
            if next_state[1] == 0 and action == -1:
                if self._q[state_id][1] < self._q[state_id][0]:
                    action = 0
                else:
                    action = 1
            if action >= 1:
                ''' buy'''
                stock += action
                profit = np.roll(profit, -1)
                profit[-1] = profit[-2] - action * self._pred[date]
            elif action == -1:
                ''' commit(sell all stock)'''
                profit = np.roll(profit, -1)
                profit[-1] = profit[-2] + stock * self._pred[date]
                stock = 0
            else:
                ''' hold'''
                profit = np.roll(profit, -1)
                profit[-1] = profit[-2]
            sharp_ratio = profit[-1] / np.std(np.diff(profit)) if np.std(profit[:-1]) != 0 else 0
            print('SR: %f'%sharp_ratio)
            print('state: %s'%str(next_state))
            print('%s: action: %d: %s'%(date, action, self._q[state_id]))
            print('%s: profit: %f'%(date, profit[-1]))
            f.write('SR: %f\n'%sharp_ratio)
            f.write('state: %s\n'%str(next_state))
            f.write('%s: action: %d: %s\n'%(date, action, self._q[state_id]))
            f.write('%s: profit: %f\n'%(date, profit[-1]))
        f.close()

    def save_Qtable(self, ticker_symbol):
        with open('models/q-table_%s.pickle'%ticker_symbol, 'wb') as f:
            pickle.dump(self._q, f)
        with open('models/states_%s.pickle'%ticker_symbol, 'wb') as f:
            pickle.dump(self._states, f)

    def load_Qtable(self, ticker_symbol):
        with open('models/q-table_%s.pickle'%ticker_symbol, 'rb') as f:
            self._q = pickle.load(f)
        with open('models/states_%s.pickle'%ticker_symbol, 'rb') as f:
            self._states = pickle.load(f)

if __name__=='__main__':
    if len(sys.argv) != 4:
        ''' Episorde'''
        print('エピソードの繰り返し回数を指定してください')
        print('銘柄コードを指定してください')
        print('実行モードを指定してください')
        print('python calc_return7.py [number of episorde] [ticker_symbol] [mode of execute]')
        sys.exit()
    num = int(sys.argv[1])   # Number of episorde
    ticker_symbol = sys.argv[2]
    mode = sys.argv[3]
    train_data = common.readClose(ticker_symbol, 0, 300)
    pred_data = common.readClose(ticker_symbol, 300, 360)
    rl = ReinforcementLearning(train_data, pred_data)
    if mode == 'train':
        rl.training(num)
        rl.save_Qtable(ticker_symbol)
    else:
        rl.load_Qtable(ticker_symbol)
    rl.predict()
