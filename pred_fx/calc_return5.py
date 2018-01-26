# Dyna-Q
import os
import sys
import random
import numpy as np
import common_functions as common

'''
Action: a in {buy: 1, hold: 0, sell: -1}
State : n in INT: portfolio < n*p_stdev
'''
class ReinforcementLearning:
    ''' Constructor'''
    def __init__(self, train_data, test_data):
        self._close = common.readClose('7203')
        self._portfolios = {date: 0 for date in self._close.keys()}
        self._alp = 0.2     # Learning rate
        self._gam = 0.9     # Discount rate
        self._span = 20     # Spans for standerd devision
        ''' Init'''
        self._state = 0     # Initial State
        self._act = 0       # 0 is hold
        self._q = {0: {1: 0, 0: 0, -1: 0}}       # Q-Table
        self._model = {0: {'reward': 0, 'state': 0}}

    def _eps_greedy(self, state):
        action = random.randint(-1, 0, 1)
        if random.random() > 0.001:
            action = max(self._q[state], key=self._q[state].get)
        return action

    def _get_start_pos(self, date_list, date):
        for idx in range(len(date_list)):
            if date_list[idx] == date:
                pos_start = idx
                break
        return pos_start

    def _exprimental(self, date, action):
        reward, state = 0, 0
        date_list = list(self._close.keys())
        pos_start = self._get_start_pos(date_list, date)
        if action == 1:
            ''' buy '''
            reward += self._close[date]
            self._portfolios[date_list[pos_start+1]] += reward
            np.array([self._portfolios[key] for key in list(self._close.keys())[pos_start:pos_start+self._span])
        elif action == -1:
            ''' sell '''

        elif action == 0:
            ''' hold '''

        return reward, state

    def main(self):
        for date in list(self._close.keys())[self._span:]:
            prev_20 = np.array([self._portfolios[key] for key in list(self._close.keys())[:self._span]])
            risk = np.std(prev_20)  # 標準偏差の算出
            current = int(self._portfolios[date]/risk if risk!=0 else 0)+1
            if current not in self._q:
                    self._q[current] = {1: 0, 0: 0, -1: 0}
            action = self._eps_greedy(current)
            reward, next_state = self._exprimental(date, action)
            self._model[current] = {'reward': reward, 'state': next_state}

if __name__=='__main__':
    rl = ReinforcementLearning('', '')
    rl.main()
