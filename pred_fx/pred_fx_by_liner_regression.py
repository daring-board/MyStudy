import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pylab as plt
import seaborn as sns
from sklearn import linear_model, tree
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
import time

def addMoveMean(data2):
    # 5日移動平均を追加します
    data2 = np.c_[data2, np.zeros((len(data2),1))] # 列の追加
    ave_day = 5
    for i in range(ave_day, len(data2)):
        tmp =data2[i-ave_day+1:i+1,4].astype(np.float) # pythonは0番目からindexが始まります
        data2[i,5] = np.mean(tmp)
    # 25日移動平均を追加します
    data2 = np.c_[data2, np.zeros((len(data2),1))]
    ave_day = 25
    for i in range(ave_day, len(data2)):
        tmp =data2[i-ave_day+1:i+1,4].astype(np.float)
        data2[i,6] = np.mean(tmp)
    # 75日移動平均を追加します
    data2 = np.c_[data2, np.zeros((len(data2),1))] # 列の追加
    ave_day = 75
    for i in range(ave_day, len(data2)):
        tmp =data2[i-ave_day+1:i+1,4].astype(np.float)
        data2[i,7] = np.mean(tmp)
    # 200日移動平均を追加します
    data2 = np.c_[data2, np.zeros((len(data2),1))] # 列の追加
    ave_day = 200
    for i in range(ave_day, len(data2)):
        tmp =data2[i-ave_day+1:i+1,4].astype(np.float)
        data2[i,8] = np.mean(tmp)
    return data2

def addTable(data2):
    # 一目均衡表を追加します (9,26, 52) (2, 5, 8)
    para1 = 9
    para2 = 26
    para3 = 52
    # 転換線 = （過去(para1)日間の高値 + 安値） ÷ 2
    data2 = np.c_[data2, np.zeros((len(data2),1))] # 列の追加
    for i in range(para1, len(data2)):
        tmp_high =data2[i-para1+1:i+1,2].astype(np.float)
        tmp_low =data2[i-para1+1:i+1,3].astype(np.float)
        data2[i,9] = (np.max(tmp_high) + np.min(tmp_low)) / 2
    # 基準線 = （過去(para2)日間の高値 + 安値） ÷ 2
    data2 = np.c_[data2, np.zeros((len(data2),1))]
    for i in range(para2, len(data2)):
        tmp_high =data2[i-para2+1:i+1,2].astype(np.float)
        tmp_low =data2[i-para2+1:i+1,3].astype(np.float)
        data2[i,10] = (np.max(tmp_high) + np.min(tmp_low)) / 2
    # 先行スパン1 = ｛ （転換値+基準値） ÷ 2 ｝を(para2)日先にずらしたもの
    data2 = np.c_[data2, np.zeros((len(data2),1))]
    for i in range(0, len(data2)-para2):
        tmp =(data2[i,9] + data2[i,10]) / 2
        data2[i+para2,11] = tmp
    # 先行スパン2 = ｛ （過去(para3)日間の高値+安値） ÷ 2 ｝を(para2)日先にずらしたもの
    data2 = np.c_[data2, np.zeros((len(data2),1))]
    for i in range(para3, len(data2)-para2):
        tmp_high =data2[i-para3+1:i+1,2].astype(np.float)
        tmp_low =data2[i-para3+1:i+1,3].astype(np.float)
        data2[i+para2,12] = (np.max(tmp_high) + np.min(tmp_low)) / 2
    # 25日ボリンジャーバンド（±1, 2シグマ）を追加します
    parab = 25
    data2 = np.c_[data2, np.zeros((len(data2),4))] # 列の追加
    for i in range(parab, len(data2)):
        tmp = data2[i-parab+1:i+1,4].astype(np.float)
        data2[i,13] = np.mean(tmp) + 1.0* np.std(tmp)
        data2[i,14] = np.mean(tmp) - 1.0* np.std(tmp)
        data2[i,15] = np.mean(tmp) + 2.0* np.std(tmp)
        data2[i,16] = np.mean(tmp) - 2.0* np.std(tmp)
    return(data2)

if __name__=='__main__':
    data_dir = './data/'
    data = pd.read_csv(data_dir + 'USDJPY_1997_2017.csv')
    data2 = np.array(data)
    data2 = addMoveMean(data2)
    data2 = addTable(data2)

    day_ago = 25
    num_var = 13
    X = np.zeros((len(data2), day_ago*num_var))
    for s in range(num_var):
        for i in range(day_ago):
            X[i: len(data2), day_ago*s+i] = data2[0: len(data2)-i, s+4]
    y = np.zeros(len(data2))
    pred_day = 10
    y[0: len(y) - pred_day] = X[pred_day: len(X), 0] - X[0: len(X)-pred_day, 0]

    # 正規化
    original_X = np.copy(X)
    tmp_mean = np.zeros(len(X))
    for i in range(day_ago, len(X)):
        tmp_mean[i] = np.mean(original_X[i-day_ago+1:i+1, 0])
        for j in range(0, X.shape[1]): X[i,j] = X[i,j]-tmp_mean[i]

    X_train = X[200: 5193, :]
    y_train = y[200: 5193]

    X_test = X[5193: len(X)-pred_day, :]
    y_test = y[5193: len(y)-pred_day]

    print('Regressor')
    start = time.time()
#    model = linear_model.LinearRegression()
#    path = './result/liner_model.csv'
    model = RandomForestRegressor(n_estimators=500, max_depth=6, min_samples_split=2)
    path = './result/random_forest.csv'
#    model = SVR(C=1e3, cache_size=200, gamma=0.2, epsilon=0.1, kernel='rbf')
#    path = './result/support_vector.csv'
#    model = tree.DecisionTreeRegressor(max_depth=8)
#    path = './result/decision_tree.csv'
#    layers = (50, 4) # 50～55、6～7 logistic
#    layers = (100, 20, 5) #tanh
#    model = MLPRegressor(hidden_layer_sizes=layers, activation='logistic', random_state=30)
    model.fit(X_train, y_train)
    elapsed_time = time.time() - start

    y_pred = model.predict(X_test)

    f = open(path, 'w', encoding='utf-8')
    f.write('pred, answer, high_and_row\n')
    for i in range(len(y_pred)):
        f.write('%s, %s, %s\n'%(y_pred[i], y_test[i], (y_pred[i] * y_test[i] >= 0)))

    result = pd.DataFrame(y_pred)
    result.columns = ['y_pred']
    result['y_test'] = y_test

    success_num = 0
    for i in range(len(y_pred)):
        if y_pred[i] * y_test[i] >= 0: success_num += 1
    print("予測日数："+ str(len(y_pred))+"、正答日数："+str(success_num)+"、正答率："+str(success_num/len(y_pred)*100))
    f.write("予測日数："+ str(len(y_pred))+"、正答日数："+str(success_num)+"、正答率："+str(success_num/len(y_pred)*100)+'\n')

    # 2017年の予測結果の合計を計算ーーーーーーーーー
    # 前々日終値に比べて前日終値が高い場合は、買いとする
    sum_2017 = 0
    for i in range(0,len(y_test)): # len()で要素数を取得しています
        if y_pred[i] >= 0: sum_2017 += y_test[i]
        else: sum_2017 -= y_test[i]
    print("2017年の利益合計：%1.3lf" %sum_2017)
    f.write("2017年の利益合計：%1.3lf\n" %sum_2017)
    # 予測結果の総和グラフを描くーーーーーーーーー
    total_return = np.zeros(len(y_test))
    # 2017年の初日を格納
    if y_pred[i] >=0: total_return[0] = y_test[i]
    else: total_return[0] = -y_test[i]
    for i in range(1, len(result)): # 2017年の2日以降を格納
        if y_pred[i] >=0:
            total_return[i] = total_return[i-1] + y_test[i]
        else:
            total_return[i] = total_return[i-1] - y_test[i]
    plt.plot(total_return)
    plt.show()

    f.write("elapsed_time:{0}".format(elapsed_time) + "[sec]\n")
    f.close()
