def getStocks():
    input_path = './data/Close/'
    dir_list = os.listdir(input_path)
    stocks = [item.split('.')[0] for item in dir_list]
    return stocks

def readClose(stock):
    path = './data/Close/%s.csv'%stock
    datas = [line.strip().split(',') for line in open(path, 'r', encoding='utf-8')][1:]
    dic = {row[1]: float(row[2]) for row in datas}
    return dic