import numpy as np
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn import datasets
from sklearn.metrics import mean_squared_error, explained_variance_score
from sklearn.utils import shuffle
import matplotlib.pyplot as plt

def plot_feature_importances(feature_importances, title, feature_names):
    # preprocess
    feature_importances = 100.0 * (feature_importances / max(feature_importances))
    index_sorted = np.flipud(np.argsort(feature_importances))
    pos = np.arange(index_sorted.shape[0]) * 0.5

    # plot graph
    plt.figure()
    plt.bar(pos, feature_importances[index_sorted], align='center')
    plt.xticks(pos, feature_names[index_sorted])
    plt.ylabel('Relative Importance')
    plt.title(title)
    plt.show()

if __name__=='__main__':
    housing_data = datasets.load_boston()
    f = open('data.txt', 'w', encoding='utf-8')
    f.write(housing_data['DESCR'])
    f.close()
    X, y = shuffle(housing_data.data, housing_data.target, random_state=7)
    num_training = int(0.8*len(X))
    X_train, y_train = X[:num_training], y[:num_training]
    X_test, y_test = X[num_training:], y[num_training:]
    dt_regressor = DecisionTreeRegressor(max_depth=4)
    dt_regressor.fit(X_train, y_train)
    ad_regressor = AdaBoostRegressor(dt_regressor, n_estimators=400, random_state=7)
    ad_regressor.fit(X_train, y_train)

    y_pred_dt = dt_regressor.predict(X_test)
    error = mean_squared_error(y_test, y_pred_dt)
    score = explained_variance_score(y_test, y_pred_dt)
    print('\n### Decision Treee Performance ###')
    print('Mean of Squared Error =', error)
    print('Explained Variance =', score)

    y_pred_ad = ad_regressor.predict(X_test)
    error = mean_squared_error(y_test, y_pred_ad)
    score = explained_variance_score(y_test, y_pred_ad)
    print('\n### AdaBoost Performance ###\n')
    print('Mean of Squared Error =', error)
    print('Explained Variance =', score)

    plot_feature_importances(
        dt_regressor.feature_importances_,
        'Distribution from DecisionTree',
        housing_data.feature_names
    )

    plot_feature_importances(
        ad_regressor.feature_importances_,
        'Distribution from AdaBoost',
        housing_data.feature_names
    )
