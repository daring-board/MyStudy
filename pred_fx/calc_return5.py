# Dyna-Q
import os
import sys
import random
import numpy as np
import common_functions as common

'''
Action: a in {buy: 1, hold: 0, sell: -1}
State : (risk, stock) risk, stock in INT: risk = p_stdev, stock = number of stock
'''
class ReinforcementLearning:
    ''' Constructor'''
    def __init__(self, train_data, test_data):
        self._close = train_data
        self._pred = test_data
        self._portfolios = {date: 0 for date in self._close.keys()}
        self._alp = 0.2     # Learning rate
        self._gam = 0.6     # Discount rate
        self._span = 20     # Spans for standerd devision
        self._div = 0.5     # State divide 状態の分割単位：標準偏差の0.5倍分割
        self._myu = 1.0     # リスク調整係数
        ''' Init'''
        self._state = 0     # Initial State
        self._act = 0       # 0 is hold
        self._q = {0: {1: 0, 0: 0, -1: 0}}       # Q-Table
        self._model = {0: {
                         1: {'reward': 0, 'state': 0},
                         0: {'reward': 0, 'state': 0},
                        -1: {'reward': 0, 'state': 0},
                      }}

    def _eps_greedy(self, state):
        action = random.choice([-1, 0, 1])
        if random.random() > 0.1:
            action = max(self._q[state], key=self._q[state].get)
        return action

    def _get_start_pos(self, date_list, date):
        for idx in range(len(date_list)):
            if date_list[idx] == date:
                pos = idx
                break
        return pos

    def _exprimental(self, date, action):
        reward, state = 0, 0
        date_list = list(self._close.keys())
        pos_today = self._get_start_pos(date_list, date)
        pre_date = date_list[pos_today-1]
        reward = action*self._close[date]
        self._portfolios[date_list[pos_today+1]] += reward
        prev_20 = np.array([self._portfolios[key] for key in list(self._close.keys())[pos_today-self._span: pos_today]])
        risk = self._myu * np.std(prev_20)
        tmp = self._portfolios[date]/risk if risk!=0 else 0
        tmp = int(tmp/self._div)
        state = tmp+1
        return reward, state

    def _is_exist_state(self, state):
        if state not in self._q:
            self._q[state] = {1: 0, 0: 0, -1: 0}
            self._model[state] = {
                                     1: {'reward': 0, 'state': 0},
                                     0: {'reward': 0, 'state': 0},
                                    -1: {'reward': 0, 'state': 0},
                                 }

    def training(self):
        for i in range(100):
            ''' Episorde start '''
            for date in list(self._close.keys())[self._span:-1]:
                date_list = list(self._close.keys())
                pos_today = self._get_start_pos(date_list, date)
                pre_date = date_list[pos_today-1]
                prev_20 = np.array([self._portfolios[key] for key in list(self._close.keys())[pos_today-self._span: pos_today]])
                risk = self._myu * np.std(prev_20)  # 標準偏差の算出
                #print('portfolio: %f, risk: %f'%(self._portfolios[date], risk))
                tmp = self._portfolios[pre_date]/risk if risk!=0 else 0
                tmp = int(tmp/self._div)
                current = tmp+1
                self._is_exist_state(current)
                action = self._eps_greedy(current)
                reward, next_state = self._exprimental(date, action)
                self._is_exist_state(next_state)
                ''' Direct ReinforcementLearning '''
                max_q = max(self._q[next_state].values())
                self._q[current][action] += self._alp*(reward+self._gam*max_q-self._q[current][action])
                ''' Update Model '''
                self._model[current][action] = {'reward': reward, 'state': next_state}
                # for key in self._q.keys(): print('%d: %s'%(key, str(self._q[key])))
                # for key in self._model.keys(): print('%d: %s'%(key, str(self._model[key])))
                ''' Plannning '''
                for j in range(100):
                    state = random.choice(list(self._q.keys()))
                    action = random.choice([-1, 0, 1])
                    reward, next_state = self._model[state][action]['reward'], self._model[state][action]['state']
                    max_q = max(self._q[next_state].values())
                    self._q[state][action] += self._alp*(reward+self._gam*max_q-self._q[state][action])
            print('episorde: %d, Q-table size: %d'%(i, len(self._q)))
            for key in self._q.keys(): print('%d: %s'%(key, str(self._q[key])))

    def predict(self):
        train_list = list(self._close.keys())
        date_list = list(self._pred.keys())
        for date in date_list:
            d_list = train_list + date_list
            pos_today = self._get_start_pos(d_list, date)
            pre_date = d_list[pos_today-1]
            prev_20 = np.array([self._portfolios[key] for key in d_list[pos_today-self._span: pos_today]])
            risk = self._myu * np.std(prev_20)  # 標準偏差の算出
            #print('portfolio: %f, risk: %f'%(self._portfolios[date], risk))
            tmp = self._portfolios[pre_date]/risk if risk!=0 else 0
            tmp = int(tmp/self._div)
            state = tmp+1
            action = 0
            if state in self._q:
                action = max(self._q[state], key=self._q[state].get)
            print('%s: action: %d: %s'%(date, action, self._q[state]))
            self._portfolios[date] = self._portfolios[pre_date]+action*self._pred[date]

if __name__=='__main__':
    train_data = common.readClose('7203', 0, 300)
    pred_data = common.readClose('7203', 300, 360)
    rl = ReinforcementLearning(train_data, pred_data)
    rl.training()
    rl.predict()
