# Dyna-Q
import os
import sys
import random
import pickle
import numpy as np
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
        self._alp = 0.2     # Learning rate
        self._gam = 0.9     # Discount rate
        self._span = 21     # Spans for standerd devision
        self._div = 0.5     # State divide 状態の分割単位：標準偏差の0.5倍分割
        self._tax = 0.002    # 手数料0.002%
        self._myu = 1.0     # リスク調整係数
        ''' Init'''
        self._states = {0: (0, 0)}
        self._q = {0: {1: 0, 0: 0, -1: 0}}       # Q-Table
        self._model = {0: {
                         1: {'reward': 0, 'state': 0},
                         0: {'reward': 0, 'state': 0},
                        -1: {'reward': 0, 'state': 0},
                      }}

    def _eps_greedy(self, state_id):
        state = self._states[state_id]
        action = random.choice([-1, 0, 1])
        if random.random() > 0.001:
            action = max(self._q[state_id], key=self._q[state_id].get)
        # if action == 1 and state[1] >= 30:
        #     action = 0
        return action

    def _get_start_pos(self, date_list, date):
        for idx in range(len(date_list)):
            if date_list[idx] == date:
                pos = idx
                break
        return pos

    def _calc_risk(self, date):
        prices = {}
        prices.update(self._close)
        prices.update(self._pred)
        date_list = list(self._close.keys())+list(self._pred.keys())
        pos_today = self._get_start_pos(date_list, date)
        prev_20 = np.array([prices[d] for d in date_list[pos_today-self._span: pos_today-1]])
        mean = np.mean(prev_20)
        std = np.std(prev_20)
        return std, mean

    def _exprimental(self, date, state_id, action):
        date_list = list(self._close.keys())+list(self._pred.keys())
        pos_today = self._get_start_pos(date_list, date)
        p_t = self._p[date]
        stock = self._states[state_id][1]
        std, mean = self._calc_risk(date)
        std = 1 if std == 0 else std
        if action == 0:
            ''' hold'''
            p_t1 = p_t + (stock * self._close[date])/std
        elif action == 1:
            ''' buy'''
            stock += 1
            p_t1 = (p_t - self._close[date]) + (stock * self._close[date])/std
        elif action == -1:
            ''' commit'''
            p_t1 = p_t + stock * self._close[date]
            stock = 0
        self._p[date_list[pos_today+1]] = p_t1
        reward = p_t1 / p_t - 1 if p_t != 0 else 0
        risk = abs(int((self._close[date]-mean)/(self._div*std)))
        next_state = (risk, stock)
        idx = len(self._states)
        if next_state not in self._states.values():
            self._states[idx] = next_state
        else:
            for i, s in self._states.items():
                if s == next_state: idx = i
        return reward, idx

    def _is_exist_state(self, state_id):
        if state_id in self._q: return
        self._q[state_id] = {1: 0, 0: 0, -1: 0}
        self._model[state_id] = {
                                 1: {'reward': 0, 'state': 0},
                                 0: {'reward': 0, 'state': 0},
                                -1: {'reward': 0, 'state': 0},
                             }

    def training(self):
        for i in range(700):
            current = 0 # current state id
            self._p = {date: 0 for date in (list(self._close.keys())+list(self._pred.keys()))}
            ''' Episorde start '''
            for date in list(self._close.keys())[self._span:]:
                action = self._eps_greedy(current)
                reward, next_state = self._exprimental(date, current, action)
                self._is_exist_state(next_state)
                ''' Direct ReinforcementLearning '''
                max_q = max(self._q[next_state].values())
                self._q[current][action] += self._alp*(reward+self._gam*max_q-self._q[current][action])
                ''' Update Model '''
                self._model[current][action] = {'reward': reward, 'state': next_state}
                ''' Plannning '''
                current = next_state
            print('episorde: %d, Q-table size: %d'%(i, len(self._q)))
            #for key in self._q.keys(): print('%d: %s'%(key, str(self._q[key])))
        #for key in self._states.keys(): print('%d: %s'%(key, str(self._states[key])))

    def predict(self):
        train_list = list(self._close.keys())
        date_list = list(self._pred.keys())
        profit = 0
        stock = 0
        self._p = {date: 0 for date in (list(self._close.keys())+list(self._pred.keys()))}
        ''' Episorde start '''
        for date in date_list:
            std, mean = self._calc_risk(date)
            risk = abs(int((self._pred[date]-mean)/(self._div*std)))
            next_state = (risk, stock)
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
            if action == 1:
                ''' buy'''
                stock += 1
            elif action == -1:
                ''' commit(sell all stock)'''
                profit += stock*self._pred[date]
                stock = 0
            else:
                ''' hold'''
                reward = 0
            print('state: %s'%str(next_state))
            print('%s: action: %d: %s'%(date, action, self._q[state_id]))
            print('%s: profit: %f'%(date, profit))

    def save_Qtable(self):
        with open('q-table.pickle', 'wb') as f:
            pickle.dump(self._q, f)

    def load_Qtable(self):
        with open('q-table.pickle', 'rb') as f:
            self._qs = pickle.load(f)

if __name__=='__main__':
    train_data = common.readClose('7203', 0, 300)
    pred_data = common.readClose('7203', 300, 360)
    # train_data = common.readDatas('7203', '5d', 0, 120)
    # pred_data = common.readDatas('7203', '5d', 120, 170)
    rl = ReinforcementLearning(train_data, pred_data)
    rl.training()
    # rl.save_Qtable()
    rl.predict()
