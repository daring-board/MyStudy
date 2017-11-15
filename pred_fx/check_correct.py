if __name__=='__main__':
    stocks = ['1605', '2502', '3382', '6501', '8267']
    for stock in stocks:
        print(stock)
        dir_path = './result/%s'%stock
        with open('%s/result.csv'%dir_path, 'r') as f:
            lines = [line.strip() for line in f][1:]
        actual_list = [float(line.split(',')[1]) for line in lines]
        pred_list = [float(line.split(',')[2]) for line in lines]
        day_length_list = [1, 2, 3, 4, 5, 6, 11, 16, 21, 41, 61]
        line = ''
        for l in day_length_list:
            corrects = [1 if (actual_list[idx]-actual_list[idx-l])/actual_list[idx] > 0.02 else 0 for idx in range(len(actual_list))]
            prediction = [1 if (pred_list[idx]-pred_list[idx-l])/pred_list[idx] > 0.02 else 0 for idx in range(len(pred_list))]
            count = 0
            for idx in range(len(actual_list)):
                ret = 1 if corrects[idx]==prediction[idx] else 0
                #print('%d, %d, %d'%(corrects[idx], prediction[idx], ret))
                if ret == 1: count += 1
            line += '高騰2％: %dd: 正答数: %d, 正答率: %.2f (％)\n'%(l, count, 100*count/len(actual_list))
            corrects = [1 if (actual_list[idx]-actual_list[idx-l])/actual_list[idx] < -0.02 else 0 for idx in range(len(actual_list))]
            prediction = [1 if (pred_list[idx]-pred_list[idx-l])/pred_list[idx] < -0.02 else 0 for idx in range(len(pred_list))]
            count = 0
            for idx in range(len(actual_list)):
                ret = 1 if corrects[idx]==prediction[idx] else 0
                #print('%d, %d, %d'%(corrects[idx], prediction[idx], ret))
                if ret == 1: count += 1
            line += '下落2％: %dd: 正答数: %d, 正答率: %.2f (％)\n'%(l, count, 100*count/len(actual_list))
        with open('%s/probs.txt'%dir_path, 'w') as f: f.write(line)
