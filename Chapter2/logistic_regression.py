import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt

def plot_classifier(classifier, X, y):
    X_min, X_max = min(X[:, 0])-1.0, max(X[:, 0])+1.0
    y_min, y_max = min(X[:, 1])-1.0, max(X[:, 1])+1.0
    step_size = 0.01

    X_values, y_values = np.meshgrid(np.arange(X_min, X_max, step_size), np.arange(y_min, y_max, step_size))
    mesh_output = classifier.predict(np.c_[X_values.ravel(), y_values.ravel()])
    mesh_output = mesh_output.reshape(X_values.shape)

    plt.figure()
    plt.pcolormesh(X_values, y_values, mesh_output, cmap=plt.cm.Set1)
    plt.scatter(X[:, 0], X[:, 1], c=y, edgecolors='black', linewidth=2, cmap=plt.cm.Paired)

    plt.xlim(X_values.min(), X_values.max())
    plt.ylim(y_values.min(), y_values.max())

    plt.xticks((np.arange(int(min(X[:, 0])-1), int(max(X[:, 0])+1), 1.0)))
    plt.xticks((np.arange(int(min(X[:, 1])-1), int(max(X[:, 1])+1), 1.0)))
    plt.show()


if __name__=='__main__':
    X = np.array([
        [4, 7], [3.5, 8], [3.1, 6.2],
        [0.5, 1], [1, 2], [1.2, 1.9],
        [6, 2], [5.7, 1.5], [5.4, 2.2],
    ])
    y = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])
    classifier = linear_model.LogisticRegression(solver='liblinear', C=1)
    classifier.fit(X, y)
    plot_classifier(classifier, X, y)
