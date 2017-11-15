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
    var = np.array([float(c_val[idx]/t_val[idx]) for idx in c_val.index])
    for idx in range(len(var)): s_val[idx] = var[idx]
    return s_val

if __name__=='__main__':
    path = './data/Close/1605.csv'
    s_val = readDatas(path)
    length = int(len(s_val)*0.8)
    train_data = s_val[:length]
    pred_data = s_val[length:]
    #print(s_val)
    plt.plot(train_data)
    # 差分系列を作成
    diff = train_data - train_data.shift()
    diff = diff.dropna()
    plt.plot(diff)
    # 対数差分系列を作成
    log_diff = np.log(train_data) - np.log(train_data.shift())
    plt.plot(log_diff)
    plt.show()
    len_lag = 100
    # 自己相関係数を求める
    s_acf = sm.tsa.stattools.acf(train_data, nlags=len_lag)
    s_pacf = sm.tsa.stattools.pacf(train_data, nlags=len_lag)

    #  自己相関のグラフ
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    fig = sm.graphics.tsa.plot_acf(train_data, lags=len_lag, ax=ax1)
    ax2 = fig.add_subplot(212)
    fig = sm.graphics.tsa.plot_pacf(train_data, lags=len_lag, ax=ax2)
    plt.show()

    res_diff = sm.tsa.arma_order_select_ic(diff, ic='aic', trend='nc')
    print(res_diff)
    arima_312 = ARIMA(train_data, order=(3,0,2)).fit(dist=False)
    print(arima_312.params)

    # 残差のチェック
    # SARIMAじゃないので、周期性が残ってしまっている。。。
    resid = arima_312.resid
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    fig = sm.graphics.tsa.plot_acf(resid.values.squeeze(), lags=len_lag, ax=ax1)
    ax2 = fig.add_subplot(212)
    fig = sm.graphics.tsa.plot_pacf(resid, lags=len_lag, ax=ax2)
    plt.show()

    pred = arima_312.predict(pred_data)
    plt.plot(s_val)
    plt.plot(pred)
    plt.show()
