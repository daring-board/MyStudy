import os
import gc
import sys
import os.path
import quandl
import numpy as np
import pandas as pd
from matplotlib import pylab as plt
from multiprocessing import Pool
from fbprophet import Prophet
import configparser as cp

config = cp.SafeConfigParser()
config.read('./config.ini')

class PredVolatGraphs():
    '''
    Class PredVolatGraphs
    Predict stock price volatility graphs
    '''
    def __init__(self, path):
        self.__input_path = path
        self.__dlen_list = [5, 10, 20]
        self.__rows = 240
        self.__pred_num = 5
        self.__periods = 60

    def readDatas(self, stock):
        df = pd.read_csv('data/Close/%s.csv'%stock)
        df = pd.concat([df['ds'], df['y']], axis=1)
        df1 = pd.read_csv('data/1592.csv')
        df1 = pd.concat([df1['ds'], df1['y']], axis=1)
        df['y'] = df['y'].divide(df1['y'])
        print(df)
        max_vals = [max(df['y']) for idx in range(len(df['ds']))]
        df['cap'] = max_vals
        df.index = range(1, len(df['ds'])+1)
        return df

    def main(self, stock):
        spans = int(120/self.__pred_num)
        dir_path = './result/%s'%stock
        if not os.path.exists(dir_path): os.makedirs(dir_path)
        s_val = self.readDatas(stock)
        for span in range(spans):
            start = self.__pred_num*span
            end = start+self.__rows
            train_data = s_val[start: end]
            model = Prophet(
                growth='logistic',
                changepoint_prior_scale=0.1,
                n_changepoints=50,
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=True
            )
            model.fit(train_data)

            future = model.make_future_dataframe(periods=self.__periods)
            future['cap'] = [train_data['cap'][start+1] for idx in range(len(future))]
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
                    if span == 0: f.write('date,actual,predict,error,confidence_interval,trend\n')
                    for idx in range(1, pred_date+1):
                        row_idx = end+idx
                        date = s_val['ds'][row_idx]
                        f_idx = forecast[forecast['ds'] == date].index[0]
                        line = '%s, %f, %f'%(s_val['ds'][row_idx], s_val['y'][row_idx], forecast['yhat'][f_idx])
                        line += ', %f, (%f_%f)'%( abs(s_val['y'][row_idx]-forecast['yhat'][f_idx]), forecast['yhat_lower'][f_idx], forecast['yhat_upper'][f_idx])
                        line += ', %f\n'%forecast['trend'][f_idx]
                        f.write(line)
                    d_term = {5: 23, 10: 11, 20: 5}
                    print((span*self.__pred_num)/pred_date)
                    if (span*self.__pred_num)/pred_date == d_term[pred_date]:
                        row_idx = end+pred_date
                        date = s_val['ds'][row_idx]
                        start = forecast[forecast['ds'] == date].index[0]+1
                        for idx in range(start, len(forecast)):
                            date = str(forecast['ds'][idx])[:-9]
                            line = '%s, %s, %f'%(date, '-', forecast['yhat'][idx])
                            line += ', %s, (%f_%f)'%( '-', forecast['yhat_lower'][idx], forecast['yhat_upper'][idx])
                            line += ', %f\n'%forecast['trend'][idx]
                            f.write(line)
            del forecast
            del future
            del model
            gc.collect()

def getStocks(dir_path):
    dir_list = os.listdir(dir_path)
    stocks = [item.split('.')[0] for item in dir_list]
    return stocks

if __name__=='__main__':
    path = './data/Close/'
    stocks = getStocks(path)
    pvg = PredVolatGraphs(path)
    if len(sys.argv) == 2:
        pvg.main(sys.argv[1])
    else:
        p = Pool(4)
        p.map_async(pvg.main, stocks).get(999999)
        p.close()
#    for stock in stocks: pvg.main(stock)
