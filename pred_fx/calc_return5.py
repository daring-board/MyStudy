import sys
import chainer
import chainer.functions as F
import chainer.links as L
import chainerrl
import random
import numpy as np
from scipy import signal
import common_functions as common

'''
Action: a in {buy(large): 3, buy(midium): 2, buy(small) 1, hold: 0, commit: -1}
State : (risk, stock) risk in  Rational Number, stock in Integer: risk = p_stdev, stock = number of stock
'''
class QFunction(chainer.Chain):
    def __init__(self, obs_size, n_actions, n_hidden_channels=50):
        super().__init__(#python3.x用
            l0=L.Linear(obs_size, n_hidden_channels),
            l1=L.Linear(n_hidden_channels,n_hidden_channels),
            l2=L.Linear(n_hidden_channels, n_actions))

    def __call__(self, x, test=False):
        """
        x ; 観測
        test : テストモードかどうかのフラグ
        """
        h = F.tanh(self.l0(x))
        h = F.tanh(self.l1(h))
        return chainerrl.action_value.DiscreteActionValue(self.l2(h))

class Enviroment():
    def __init__(self, train_data, test_data):
        self._close = train_data
        self._pred = test_data
        self._p = {date: 0 for date in (list(self._close.keys())+list(self._pred.keys()))}
        self._alp = 0.2         # Learning rate
        self._gam = 0.9         # Discount rate
        self._span = 21         # Spans for standerd devision
        self._div = 0.5         # State divide 状態の分割単位：標準偏差の0.5倍分割
        self._tax = 0.002       # 手数料0.002%
        self._f = 0.9           # 投資比率
        self._init = 100000     # 初期投資
        ''' Init'''
        self._actions = [-1, 0, 1, 2, 3]
        self._states = {0: [0, 0, 0]}
        self._q = {0: {act: 0 for act in self._actions}}       # Q-Table
        self._model = {0: {act: {'reward': 0, 'state': 0} for act in self._actions}}
        ''' Parameter '''
        self._current = 0
        self._date = list(self._close.keys())[0]

    def sample(self):
        date_list = list(self._close.keys())+list(self._pred.keys())
        pos_today = self._get_start_pos(date_list)
        yesterday = date_list[pos_today-1]
        state = self._states[self._current]
        action = random.choice(self._actions)
        if action >= 1 and state[1] >= 9:
            action = random.choice(self._actions[:2])
        if action == -1 and state[1] == 0:
            action = 0
        return action

    def reset(self):
        self._p = {date: 0 for date in (list(self._close.keys())+list(self._pred.keys()))}
        self._p[list(self._close.keys())[self._span]] = self._init
        self._current = 0
        self._date = list(self._close.keys())[0]
        return self._current

    def _get_start_pos(self, date_list):
        for idx in range(len(date_list)):
            if date_list[idx] == self._date:
                pos = idx
                break
        return pos

    def _calc_stats(self):
        prices = {}
        prices.update(self._close)
        prices.update(self._pred)
        date_list = list(self._close.keys())+list(self._pred.keys())
        pos_today = self._get_start_pos(date_list)
        prev_20 = np.array([prices[d] for d in date_list[pos_today-self._span: pos_today-1]])
        mean = np.mean(prev_20)
        std = np.std(prev_20)
        trend = prev_20 - signal.detrend(prev_20)
        return std, mean, np.diff(trend)[0]

    def set_date(self, date):
        self._date = date

    def get_state(self, state_id):
        return self._states[state_id]

    def step(self, action, mode):
        date_list = list(self._close.keys())+list(self._pred.keys())
        prices = self._close if mode == 'train' else self._pred
        pos_today = self._get_start_pos(date_list)
        p_t = self._p[self._date]
        stock = self._states[self._current][1]
        std, mean, trend = self._calc_stats()
        risk = abs(prices[date_list[pos_today-1]] - mean) / (self._div * std)
        risk = 1 if risk == 0 else risk
        if action == 0:
            ''' hold'''
            p_t1 = p_t + (stock * prices[self._date]) / risk
        elif action >= 1:
            ''' buy'''
            stock += action
            p_t1 = (p_t - prices[self._date]) + ((stock - self._tax) * prices[self._date]) / risk
        elif action == -1:
            ''' commit'''
            p_t1 = p_t + (stock - self._tax) * prices[self._date]
            stock = 0
        self._p[date_list[pos_today+1]] = p_t1
        reward = p_t1 / p_t - 1 if p_t != 0 else 0
        next_state = [risk, stock, trend]
        idx = len(self._states)
        if next_state not in self._states.values():
            self._states[idx] = next_state
        else:
            for i, s in self._states.items():
                if s == next_state:
                    idx = i
        return reward, idx, True if self._date == list(prices.keys())[-1] else False, ''

if __name__=='__main__':
    if len(sys.argv) != 4:
        ''' Episorde'''
        print('エピソードの繰り返し回数を指定してください')
        print('銘柄コードを指定してください')
        print('実行モードを指定してください')
        print('python calc_return5.py [number of episorde] [ticker_symbol] [mode of execute]')
        sys.exit()
    num = int(sys.argv[1])   # Number of episorde
    ticker_symbol = sys.argv[2]
    mode = sys.argv[3]
    train_data = common.readClose(ticker_symbol, 0, 300)
    pred_data = common.readClose(ticker_symbol, 300, 360)
    env = Enviroment(train_data, pred_data)

    obs_size = len(env._states[0])
    n_actions = len(env._actions)
    q_func = QFunction(obs_size, n_actions)
    # q_func.to_gpu(0) ## GPUを使いたい人はこのコメントを外す

    optimizer = chainer.optimizers.Adam(eps=1e-2)
    optimizer.setup(q_func) #設計したq関数の最適化にAdamを使う
    gamma = 0.9
    explorer = chainerrl.explorers.ConstantEpsilonGreedy(
        epsilon=0.2, random_action_func=env.sample)
    replay_buffer = chainerrl.replay_buffer.ReplayBuffer(capacity = 10**6)

    agent = chainerrl.agents.DoubleDQN(
    q_func, optimizer, replay_buffer, gamma, explorer,
    replay_start_size=500)

    if mode == 'train':
        for idx in range(1, num+1):
            current = env.reset()
            reward = 0
            for date in list(env._close.keys())[env._span:]:
                state = np.array(env.get_state(current))
                state = state.astype(np.float32)
                action = agent.act_and_train(state, reward)
                env.set_date(date)
                reward, current, done, info = env.step(action, 'train')
            print('episorde: %d'%idx)
            print(agent.get_statistics())
        agent.save('models/%s_model'%ticker_symbol)

    print('Test start')
    if mode != 'train':
        agent.load('models/%s_model'%ticker_symbol)
    whole = 100000
    stock = 0
    date_list = list(env._close.keys())+list(env._pred.keys())
    env.set_date(list(env._pred.keys())[1])
    std, mean, trend = env._calc_stats()
    pos_today = env._get_start_pos(date_list)
    risk = abs(env._pred[date_list[pos_today-1]]-mean)/(env._div*std)
    next_state = (risk, 0, trend)
    for date in list(env._pred.keys())[1:]:
        env.set_date(date)
        std, mean, trend = env._calc_stats()
        pos_today = env._get_start_pos(date_list)
        risk = abs(env._pred[date_list[pos_today-1]]-mean)/(env._div*std)
        state = np.array((risk, stock, trend))
        state = state.astype(np.float32)
        action = agent.act(state)
        env.set_date(date)
        print(state)
        act = env._actions[action]
        print('%s: %d'%(date, act))
        if act >= 1:
            ''' buy'''
            whole -= act * pred_data[date]
            stock += act
        elif act == -1:
            ''' commit(sell all stock)'''
            whole += state[1] * pred_data[date]
            stock = 0
        else:
            ''' hold'''
        print(whole)
