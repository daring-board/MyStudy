import os
import gc
import sys
import os.path
import numpy as np
import pandas as pd
from matplotlib import pylab as plt
from fbprophet import Prophet

class PredVolatGraphs():
    '''
    Class PredVolatGraphs
    Predict stock price volatility graphs
    '''
    def __init__(self):
        self.__input_path = './data/Close/'
        self.__dlen_list = [5, 10, 15, 20, 40, 60]
        self.__rows = 240
        self.__pred_num = 5
        self.extra_num = 1160
        self.__periods = 60

    def getStocks(self, dir_path):
        dir_list = os.listdir(dir_path)
        stocks = [item.split('.')[0] for item in dir_list]
        return stocks

    def readDatas(self, path):
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

    def main(self):
        stocks = self.getStocks(self.__input_path)[:60]
        spans = int(120/self.__pred_num)
        for stock in stocks:
            path = self.__input_path+'%s.csv'%stock
            dir_path = './result/%s'%stock
            if not os.path.exists(dir_path): os.makedirs(dir_path)
            s_val = self.readDatas(path)
            for span in range(spans):
                start = self.extra_num+self.__pred_num*span-self.__rows
                end = start+self.__rows
                train_data = s_val[start: end]
                model = Prophet(
                    growth='logistic',
                    changepoint_prior_scale=0.1,
                    n_changepoints=50,
                    yearly_seasonality=True,
                    weekly_seasonality=True,
                    daily_seasonality=True
                )
                model.fit(train_data)

                future = model.make_future_dataframe(periods=self.__periods)
                future['cap'] = [train_data['cap'][start] for idx in range(len(future))]
                forecast = model.predict(future)
                model.plot(forecast)
                filename = '%s/output%d.png'%(dir_path, span+1)
                plt.savefig(filename)
                plt.close()
                model.plot_components(forecast)
                filename = '%s/trend%s.png'%(dir_path, span+1)
                plt.savefig(filename)
                plt.close()
                for pred_date in self.__dlen_list:
                    if (span*self.__pred_num)%pred_date != 0: continue
                    with open('%s/result_%dd.csv'%(dir_path, pred_date), 'a') as f:
                        if span == 0: f.write('date, actual, predict, error, confidence_interval\n')
                        for idx in range(pred_date):
                            row_idx = end+idx
                            f_idx = len(forecast)-self.__periods+idx
                            line = '%s, %f, %f'%(s_val['ds'][row_idx], s_val['y'][row_idx],forecast['yhat'][f_idx])
                            line += ', %f, (%f_%f)\n'%( abs(s_val['y'][row_idx]-forecast['yhat'][f_idx]), forecast['yhat_lower'][f_idx], forecast['yhat_upper'][f_idx])
                            f.write(line)
                    with open('%s/trend_%dd.csv'%(dir_path, pred_date), 'a') as f:
                        if span == 0: f.write('date, trend')
                        for idx in range(pred_date):
                            row_idx = end+idx
                            f_idx = len(forecast)-self.__periods+idx
                            line = '%s, %f\n'%(s_val['ds'][row_idx], forecast['trend'][f_idx])
                            f.write(line)
                del forecast
                del future
                del model
                gc.collect()

if __name__=='__main__':
    pvg = PredVolatGraphs()
    pvg.main()
