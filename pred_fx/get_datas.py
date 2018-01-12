import sys
import quandl
import pandas as pd
import configparser as cp

config = cp.SafeConfigParser()
config.read('./config.ini')

class StockReader():

    def appendCSV(self, path, code):
        all_rows = int(config.get('config', 'all_rows'))
        data = quandl.get('TSE/%s'%code, rows=rows)
        df = pd.DataFrame({
                'ds': data.index.astype('str'),
                'y': data['Close']
            })
        df.index = range(1, int(rows)+1)
        datas = pd.read_csv('%s/%s.csv'%(path, code))
        df2 = pd.DataFrame({
                'ds': datas['ds'],
                'y': datas['y']
            })
        df = pd.concat([df2, df], axis=0)
        df.index = range(1, all_rows+int(rows)+1)
        df = df[int(rows):]
        df.index = range(1, all_rows+1)
        df.to_csv('%s/%s.csv'%(path, code), encoding='utf-8')

    def createCSV(self, path, code):
        all_rows = int(config.get('config', 'all_rows'))
        data = quandl.get('TSE/%s'%code, rows=all_rows)
        df = pd.DataFrame({
                'ds': data.index.astype('str'),
                'y': data['Close']
            })
        df.index = range(1, int(all_rows)+1)
        df.to_csv('%s/%s.csv'%(path, code), encoding='utf-8')

if __name__=='__main__':
    path = sys.argv[1] # 保存先を指定。
    mode = sys.argv[2] # データの読み込みモード。
    stocks = config.get('config', 'codes').strip().split(',')
    rows = config.get('config', 'rows')
    quandl.ApiConfig.api_key = config.get('config', 'api_key')
    reader = StockReader()
    if mode == 'append':
        reader.appendCSV('data', 1592)
        for stock in stocks: reader.appendCSV(path, stock)
    elif mode == 'create':
        reader.createCSV('data', 1592)
        for stock in stocks: reader.createCSV(path, stock)
    else:
        stock = sys.argv[3]
        reader.createCSV(path, stock)
