def getStocks():
    input_path = './data/Close/'
    dir_list = os.listdir(input_path)
    stocks = [item.split('.')[0] for item in dir_list]
    return stocks

def readClose(stock, start=0, end=360):
    path = './data/Close/%s.csv'%stock
    datas = [line.strip().split(',') for line in open(path, 'r', encoding='utf-8')][start+1:end+1]
    dic = {row[1]: float(row[2]) for row in datas}
    return dic

def readDatas(stock, noday, start=0, end=120):
    path = './result/%s/result_%s.csv'%(stock, noday)
    d = [line.split(',') for line in open(path, 'r')][start+1:end+1]
    dic = {row[0]: float(row[2]) for row in d}
    return dic
