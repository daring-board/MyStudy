import sys
import quandl
import pandas as pd
import configparser as cp

config = cp.SafeConfigParser()
config.read('./config.ini')

def createCSV(path, code):
    data = quandl.get('TSE/%s'%code, rows=rows)
    df = pd.DataFrame({
            'ds': data.index.astype('str'),
            'y': data['Close']
        })
    df.index = range(1, int(rows)+1)
    print(df)
    datas = pd.read_csv('%s/%s.csv'%(path, code))
    df2 = pd.DataFrame({
            'ds': datas['ds'],
            'y': datas['y']
        })
    print(df2)
    df = pd.concat([df2, df], axis=0)
    df.index = range(1, 360+1)
    df.to_csv('%s/%s.csv'%(path, code), encoding='utf-8')

if __name__=='__main__':
    path = sys.argv[1] # 保存先を指定。
    stocks = config.get('config', 'codes').strip().split(',')
    rows = config.get('config', 'rows')
    quandl.ApiConfig.api_key = config.get('config', 'api_key')
    createCSV('data', 1592)
    for stock in stocks: createCSV(path, stock)
