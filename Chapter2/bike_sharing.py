import sys
import csv
import numpy as np
from sklearn import preprocessing
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, explained_variance_score
from sklearn.utils import shuffle
import matplotlib.pyplot as plt
from housing_prices import plot_feature_importances

def load_dataset(filename):
    file_reader = csv.reader(open(filename, 'r'), delimiter=',')
    X, y = [], []
    for row in file_reader:
        X.append(row[2:13])
        y.append(row[-1])

    feature_names = np.array(X[0])
    return np.array(X[1:]).astype(np.float32), np.array(y[1:]).astype(np.float32), feature_names

if __name__=='__main__':
    X, y, feature_names = load_dataset(sys.argv[1])
    X, y = shuffle(X, y, random_state=7)
    num_training = int(0.9*len(X))
    X_train, y_train = X[:num_training], y[:num_training]
    X_test, y_test = X[num_training:], y[num_training:]
    rf_regressor = RandomForestRegressor(n_estimators=1000, max_depth=10, min_samples_split=2)
    rf_regressor.fit(X_train, y_train)

    y_pred_rf = rf_regressor.predict(X_test)
    error = mean_squared_error(y_test, y_pred_rf)
    score = explained_variance_score(y_test, y_pred_rf)
    print('\n### RandomForest Performance ###')
    print('Mean of Squared Error =', error)
    print('Explained Variance =', score)

    plot_feature_importances(
        rf_regressor.feature_importances_,
        'Random Forest Regressor',
        feature_names,
    )
