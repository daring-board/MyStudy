if __name__=='__main__':
    stock = '1605'
    dir_path = './result/%s'%stock
    with open('%s/result.csv'%dir_path, 'r') as f:
        lines = [line.strip() for line in f][1:]
    actual_list = [float(line.split(',')[1]) for line in lines]
    pred_list = [float(line.split(',')[2]) for line in lines]
    day_length_list = [1, 2, 3, 4, 5, 6, 11, 16, 21, 41, 61]
    corrects_list = []
    prediction_list = []
    for l in day_length_list:
        corrects = [1 if actual_list[idx]-actual_list[idx-l] > 0 else 0 for idx in range(len(actual_list))]
        prediction = [1 if pred_list[idx]-pred_list[idx-l] > 0 else 0 for idx in range(len(pred_list))]
        count = 0
        for idx in range(len(actual_list)):
            ret = 1 if corrects[idx]==prediction[idx] else 0
            #print('%d, %d, %d'%(corrects[idx], prediction[idx], ret))
            if ret == 1: count += 1
        print('%dd: 正答数: %d, 正答率: %.2f'%(l, count, 100*count/len(actual_list)))
