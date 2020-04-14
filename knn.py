import numpy as np
import os

# Machine learning API
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics

# Read log files and store model
import pickle

def transformCommand(command):
    if 'RIGHT' in str(command):
        return 2
    elif 'LEFT' in str(command):
        return 1
    return 0

def get_data(filename):
    balls = []
    commands = []
    pf_pos = []

    with open(filename, 'rb') as f:
        log = pickle.load(f)

    for scene_info in log:
        balls.append(scene_info.ball)
        commands.append(transformCommand(scene_info.command))
        pf_pos.append(scene_info.platform[0])

    balls = np.array(balls)
    vector = balls[1:] - balls[:-1]
    commands_ary = np.array([commands])
    commands_ary = commands_ary.reshape((len(commands), 1))
    pf_pos_ary = np.array([pf_pos])
    pf_pos_ary = pf_pos_ary.reshape(len(pf_pos), 1)
    return np.hstack((balls[:-1], pf_pos_ary[:-1], vector, commands_ary[:-1]))

if __name__ == '__main__':
    log_dir = '../log'
    data = None
    init = False

    for filename in os.listdir(log_dir):
        tmp = get_data(os.path.join(log_dir, filename))
        if not init:
            data = tmp
            init = True
        else:
            data = np.append(data, tmp, axis = 0)

    x = data[:, :-1]
    y = data[:,  -1]
    print('x:')
    print(len(x))
    print(x)
    print('y:')
    print(y)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2)
    knn = KNeighborsClassifier(n_neighbors = 4).fit(x_train, y_train)
    y_pred = knn.predict(x_test)
    accuracy = metrics.accuracy_score(y_test, y_pred)
    print('Accuracy: {:.2f}%'.format(accuracy * 100))

    with open('knn_model.pickle', 'wb') as f:
        pickle.dump(knn, f)

    print(len(x[y == 0]))
    print(len(x[y == 1]))
    print(len(x[y == 2]))
