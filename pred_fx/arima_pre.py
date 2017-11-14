import numpy as np
import pandas as pd
from scipy import stats
from matplotlib import pylab as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.tsa.arima_model import ARIMA
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 15, 6

def readDatas(path):
    dateparse = lambda dates: pd.datetime.strptime(dates, '%Y/%m/%d')
    close = pd.read_csv(path, index_col='日付', date_parser=dateparse, dtype='float')
    c_val = close['終値']
    path = './data/TOPIX.csv'
    topix = pd.read_csv(path, index_col='日付', date_parser=dateparse, dtype='float')
    t_val = topix['終値']
    s_val = c_val.copy()
    var = np.array([c_val[idx]/t_val[idx] for idx in c_val.index])
    for idx in range(len(var)): s_val[idx] = var[idx]
    return s_val

if __name__=='__main__':
    path = './data/Close/1605.csv'
    s_val = readDatas(path)
    print(s_val)
    # plt.plot(s_val)
    # 差分系列を作成
    diff = s_val - s_val.shift()
    diff = diff.dropna()
    # plt.plot(diff)
    # 対数差分系列を作成
    log_diff = np.log(s_val) - np.log(s_val.shift())
    # plt.plot(log_diff)
    # 自己相関係数を求める
    # s_acf = sm.tsa.stattools.acf(s_val, nlags=40)
    # s_pacf = sm.tsa.stattools.pacf(s_val, nlags=40)

    #  自己相関のグラフ
    # fig = plt.figure(figsize=(12,8))
    # ax1 = fig.add_subplot(211)
    # fig = sm.graphics.tsa.plot_acf(s_val, lags=40, ax=ax1)
    # ax2 = fig.add_subplot(212)
    # fig = sm.graphics.tsa.plot_pacf(s_val, lags=40, ax=ax2)


    res_diff = sm.tsa.arma_order_select_ic(diff, ic='aic', trend='nc')
    print(res_diff)
    arima_312 = ARIMA(s_val, order=(3,1,2)).fit(dist=False)
    #print(arima_312.params)

    # 残差のチェック
    # SARIMAじゃないので、周期性が残ってしまっている。。。
    resid = arima_312.resid
    fig = plt.figure(figsize=(12,8))
    ax1 = fig.add_subplot(211)
    fig = sm.graphics.tsa.plot_acf(resid.values.squeeze(), lags=40, ax=ax1)
    ax2 = fig.add_subplot(212)
    fig = sm.graphics.tsa.plot_pacf(resid, lags=40, ax=ax2)

    pred = arima_312.predict('2017-03-01', '2017-04-03')
    # print(pred)
    # plot(pred)
    print(s_val['2017-03-01'])
    plt.show()
