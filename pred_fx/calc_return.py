import os
import sys

def getStocks():
    input_path = './data/Close/'
    dir_list = os.listdir(input_path)
    stocks = [item.split('.')[0] for item in dir_list]
    return stocks

par = 100
extra_num = 1160
day_length_list = [5, 10, 15, 20, 40, 60]
if __name__=='__main__':
    rate = float(sys.argv[1])
    # rate = 0.05
    stocks = getStocks()[:50]
    # stocks = ['1605']
    close_path = 'data/Close/%s.csv'
    l = day_length_list[1]
    line = ''
    whole_ret = 0
    for stock in stocks:
        print(stock)
        close_file = close_path%stock
        close = [line.split(',') for line in open(close_file, 'r', encoding='utf-8')][extra_num+1:]
        date = [item[0] for item in close]
        close = [float(item[1]) for item in close]
        with open('result/%s/result_%dd.csv'%(stock, l), 'r') as f:
            lines = [line.strip() for line in f][1:]
        actual_list = [float(line.split(',')[1]) for line in lines]
        pred_list = [float(line.split(',')[2]) for line in lines]
        values = [(actual_list[idx]-actual_list[idx-l])/actual_list[idx] for idx in range(l, len(actual_list))]
        r_corrects = [1 if val > rate else 0 for val in values]
        values = [(pred_list[idx]-pred_list[idx-l])/pred_list[idx] for idx in range(l, len(pred_list))]
        r_preds = [1 if val > rate else 0 for val in values]
#            for idx in range(len(prediction)): print('%d, %d'%(r_corrects[idx], prediction[idx]))
        values = [(actual_list[idx]-actual_list[idx-l])/actual_list[idx] for idx in range(l, len(actual_list))]
        f_corrects = [1 if val < -rate else 0 for val in values]
        values = [(pred_list[idx]-pred_list[idx-l])/pred_list[idx] for idx in range(l, len(pred_list))]
        f_preds = [1 if val < -rate else 0 for val in values]
#            for idx in range(len(prediction)): print('%d, %d'%(f_corrects[idx], prediction[idx]))
        result = init = 10000
        stack = 0
        itl = (0, 120)
        line += 'num, date, buy, sale, price, diff\n'
        for idx in range(len(r_preds)):
            if (idx < itl[0]) or (idx >= itl[1]): continue
            pre_result = result
            if r_preds[idx]==1 and close[l+idx] < result: stack += 1
            result -= r_preds[idx]*int(close[l+idx]) if close[l+idx] < result else 0
            # if f_preds[idx]==1: stack -= 1
            """空売りしない
            if f_preds[idx]==1 and stack > 0: stack -= 1
            result += f_preds[idx]*int(close[l+idx]) if f_preds[idx]==1 and stack > 0 else 0
            """

            """空売りする"""
            if f_preds[idx]==1: stack -= 1
            result += f_preds[idx]*int(close[l+idx]) if f_preds[idx]==1 else 0

            line += '%d, %s, %d, %d, %.2f, %.2f\n'%(idx, date[idx+l], r_preds[idx], f_preds[idx], result, result-pre_result)
        #print('%0.2f + %.2f = %.2f'%(result, stack*close[len(r_preds)-1+l], result+stack*close[len(r_preds)-1+l]))
        result += stack*close[len(r_preds)-1+l]
        line += '利益: %d, 利益率(％): %.2f\n'%(result-init, par*(result-init)/init)
        whole_ret += result
    print(par*(whole_ret-init*len(stocks))/(init*len(stocks)))
    with open('result/return_%d.csv'%(par*rate), 'w', encoding='utf-8') as f: f.write(line)
