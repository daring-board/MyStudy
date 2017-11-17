import os
import sys
from matplotlib import pylab as plt

par = 100
day_length_list = [5, 10, 15, 20, 40, 60]

def getStocks():
    input_path = './data/Close/'
    dir_list = os.listdir(input_path)
    stocks = [item.split('.')[0] for item in dir_list]
    return stocks

if __name__=='__main__':
    rate = float(sys.argv[1])
    # rate = 0.05
    stocks = getStocks()[:50]
    for stock in stocks:
        print(stock)
        dir_path = './result/%s'%stock
        line = '頻度_rate, 日数, 高騰正解数, 高騰正答数, 下落正解数, 下落正答数, 高騰正答率(％), 下落正答率(％)\n'
        for l in day_length_list:
            with open('%s/result_%dd.csv'%(dir_path, l), 'r') as f:
                lines = [line.strip() for line in f][1:]
            actual_list = [float(line.split(',')[1]) for line in lines]
            pred_list = [float(line.split(',')[2]) for line in lines]
            plt.figure()
            plt.title('stock_close/topix_close')
            plt.plot(actual_list, label='actual')
            plt.plot(pred_list, label='predict')
            plt.legend()
            filename = '%s/result_graph%dd.png'%(dir_path, l)
            plt.savefig(filename)
            values = [(actual_list[idx]-actual_list[idx-l])/actual_list[idx] for idx in range(l, len(actual_list))]
            r_corrects = [1 if val > rate else 0 for val in values]
            values = [(pred_list[idx]-pred_list[idx-l])/pred_list[idx] for idx in range(l, len(pred_list))]
            prediction = [1 if val > rate else 0 for val in values]
#            for idx in range(len(prediction)): print('%d, %d'%(r_corrects[idx], prediction[idx]))
            raise_correct = sum(item for item in r_corrects)
            count_raise = sum(1 if r_corrects[idx]==prediction[idx] else 0 for idx in range(len(prediction)))
            values = [(actual_list[idx]-actual_list[idx-l])/actual_list[idx] for idx in range(l, len(actual_list))]
            f_corrects = [1 if val < -rate else 0 for val in values]
            values = [(pred_list[idx]-pred_list[idx-l])/pred_list[idx] for idx in range(l, len(pred_list))]
            prediction = [1 if val < -rate else 0 for val in values]
#            for idx in range(len(prediction)): print('%d, %d'%(f_corrects[idx], prediction[idx]))
            fall_correct = sum(item for item in f_corrects)
            count_fall = sum(1 if f_corrects[idx]==prediction[idx] else 0 for idx in range(len(prediction)))
            len_date = len(actual_list)-l
            line += '%dd_%d％,'%(l, rate*par)
            line += ' %d, %d, %d, %d, %d,'%(len_date, raise_correct, count_raise, fall_correct, count_fall)
            line += ' %.2f, %.2f\n'%(par*count_raise/len_date, par*count_fall/len_date)
        with open('%s/probs_%d.csv'%(dir_path, int(par*rate)), 'w') as f: f.write(line)
