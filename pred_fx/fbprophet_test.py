import os
import os.path
import numpy as np
import pandas as pd
from matplotlib import pylab as plt
from fbprophet import Prophet

def getStocks(dir_path):
    dir_list = os.listdir(dir_path)
    stocks = [item.split('.')[0] for item in dir_list]
    return stocks

def readDatas(path):
    dateparse = lambda dates: pd.datetime.strptime(dates, '%Y/%m/%d')
    close = pd.read_csv(path, index_col=None)
    c_val = pd.concat([close['日付'], close['終値']], axis=1)
    path = './data/TOPIX.csv'
    topix = pd.read_csv(path, index_col=None)
    t_val = pd.concat([topix['日付'], topix['終値']], axis=1)
    s_val = c_val.copy()
    var = np.array([float(c_val.ix[idx, 1]/t_val.ix[idx, 1]) for idx in c_val.index])
    for idx in range(len(var)): s_val.ix[ idx, 1] = var[idx]
    max_vals = [max(var) for idx in range(len(s_val))]
    s_val.columns = ['ds', 'y']
    s_val['cap'] = max_vals
    return s_val

if __name__=='__main__':
    input_path = './data/Close/'
    stocks = getStocks(input_path)[10:30]
    #stocks = ['1605']
    #stocks = ['1605', '2502', '3382', '6501', '8267']
    day_length_list = [5, 10, 15, 20, 40, 60]
    rows = 240
    pred_num = 5
    spans = int(120/pred_num)
    extra_num = 1160
    for stock in stocks:
        path = input_path+'%s.csv'%stock
        dir_path = './result/%s'%stock
        if not os.path.exists(dir_path): os.makedirs(dir_path)
        s_val = readDatas(path)
        for span in range(spans):
            start = extra_num+pred_num*span-rows
            end = start+rows
            train_data = s_val[start: end]
            #print(train_data)
            model = Prophet(
                growth='logistic',
                changepoint_prior_scale=0.01,
                n_changepoints=150,
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True
            )
            model.fit(train_data)

            periods = 60
            future = model.make_future_dataframe(periods=periods)
            future['cap'] = [train_data['cap'][start] for idx in range(len(future))]
            forecast = model.predict(future)
            model.plot(forecast)
            filename = '%s/output%d.png'%(dir_path, span+1)
            plt.savefig(filename)
            # print(forecast)
            for pred_date in day_length_list:
                if (span*pred_num)%pred_date != 0: continue
                with open('%s/result_%dd.csv'%(dir_path, pred_date), 'a') as f:
                    if span == 0: f.write('date, actual, predict, error, confidence_interval\n')
                    for idx in range(pred_date):
                        row_idx = end+idx
                        f_idx = len(forecast)-periods+idx
                        line = '%s, %f, %f'%(s_val['ds'][row_idx], s_val['y'][row_idx],forecast['yhat'][f_idx])
                        line += ', %f, (%f_%f)\n'%( abs(s_val['y'][row_idx]-forecast['yhat'][f_idx]), forecast['yhat_lower'][f_idx], forecast['yhat_upper'][f_idx])
                        f.write(line)
