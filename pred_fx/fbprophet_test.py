import os
import os.path
import numpy as np
import pandas as pd
from matplotlib import pylab as plt
from fbprophet import Prophet

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
    stock = '1605'
    path = './data/Close/%s.csv'%stock
    dir_path = './result/%s'%stock
    if not os.path.exists(dir_path): os.makedirs(dir_path)
    s_val = readDatas(path)
    length = int(len(s_val)*0.9)
    rows = 240
    spans = 240
    pred_num = int(rows/spans)
    extra_num = 1040
    for span in range(spans):
        start = extra_num+pred_num*span
        end = start + pred_num
        train_data = s_val[:start]
        #pred_data = s_val[start:end]
        model = Prophet(growth='logistic', yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=True)
        model.fit(train_data)

        future = model.make_future_dataframe(periods=20)
        future['cap'] = [train_data['cap'][1] for idx in range(len(future))]
        forecast = model.predict(future)
        model.plot(forecast)
        filename = '%s/output%d.png'%(dir_path, span)
        plt.savefig(filename)
        with open('%s/result.csv'%dir_path, 'a') as f:
            if span == 0: f.write('date, actual, predict, error, confidence_interval\n')
            for idx in range(pred_num):
                line = '%s, %f, %f'%(s_val['ds'][start+idx], s_val['y'][start+idx],forecast['yhat'][start+idx])
                line += ', %f, (%f_%f)\n'%( abs(s_val['y'][start+idx]-forecast['yhat'][start+idx]), forecast['yhat_lower'][start+idx], forecast['yhat_upper'][start+idx])
                f.write(line)
