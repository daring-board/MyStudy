par = 100

if __name__=='__main__':
    stocks = ['1605', '2502', '3382', '6501', '8267']
    for stock in stocks:
        print(stock)
        dir_path = './result/%s'%stock
        #rate = 0.02
        rate = 0.02
        with open('%s/result.csv'%dir_path, 'r') as f:
            lines = [line.strip() for line in f][1:]
        actual_list = [float(line.split(',')[1]) for line in lines]
        pred_list = [float(line.split(',')[2]) for line in lines]
        day_length_list = [1, 2, 3, 4, 5, 6, 11, 16, 21, 41, 61]
        line = '正解, 日数, 高騰正解数, 高騰正答数, 下落正解数, 下落正答数, 高騰正答率(％), 下落正答率(％)\n'
        for l in day_length_list:
            values = [(actual_list[idx]-actual_list[idx-l])/actual_list[idx] for idx in range(len(actual_list))]
            r_corrects = [1 if val > rate else 0 for val in values]
            values = [(pred_list[idx]-pred_list[idx-l])/pred_list[idx] for idx in range(len(pred_list))]
            prediction = [1 if val > rate else 0 for val in values]
#            for idx in range(len(prediction)): print('%d, %d'%(r_corrects[idx], prediction[idx]))
            raise_correct = sum(item for item in r_corrects)
            count_raise = sum(1 if r_corrects[idx]==prediction[idx] and r_corrects[idx]==1 else 0 for idx in range(len(actual_list)))
            values = [(actual_list[idx]-actual_list[idx-l])/actual_list[idx] for idx in range(len(actual_list))]
            f_corrects = [1 if val > -rate else 0 for val in values]
            values = [(pred_list[idx]-pred_list[idx-l])/pred_list[idx] for idx in range(len(pred_list))]
            prediction = [1 if val > -rate else 0 for val in values]
            fall_correct = sum(item for item in f_corrects)
            count_fall = sum(1 if f_corrects[idx]==prediction[idx] and f_corrects[idx]==1 else 0 for idx in range(len(actual_list)))
            line += '%dd_%d％,'%(l, rate*par)
            line += ' %d, %d, %d, %d, %d,'%(len(actual_list), raise_correct, count_raise, fall_correct, count_fall)
            line += ' %.2f, %.2f\n'%(par*count_raise/raise_correct, par*count_fall/fall_correct)
        with open('%s/probs_%d.csv'%(dir_path, int(par*rate)), 'w') as f: f.write(line)
