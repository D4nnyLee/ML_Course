#!/usr/bin/env python3

import os
import pickle

from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

def get_feature_and_answer_1p(path) -> list:

    # Initial
    ball_size = (5, 5)
    result = [[], []]
    last = 0

    with open(path, 'rb') as f:
        scene_info = pickle.load(f)

    # Iterate through all scene_info and generate feature and answer
    for idx in range(len(scene_info) - 1):
        info = scene_info[idx]

        # feature
        next_blocker = scene_info[idx + 1]['blocker']
        ball_speed = (next_blocker[0] - info['blocker'][0], next_blocker[1] - info['blocker'][1])

        result[0].append([*info['ball'], *info['ball_speed'], *info['blocker']])

        # answer
        if info['ball'][1] + ball_size[1] == info['platform_1P'][1]:
            for i in range(last, idx):
                result[1].append(info['ball'][0])

            last = idx

    result[0] = result[0][:len(result[1])]

    return result

def get_feature_and_answer_2p(path) -> list:

    # Initial
    platform_size = (40, 30)
    result = [[], []]
    last = 0

    with open(path, 'rb') as f:
        scene_info = pickle.load(f)

    # Iterate through all scene_info and generate feature and answer
    for idx in range(len(scene_info) - 1):
        info = scene_info[idx]

        # feature
        result[0].append([*info['ball'], *info['ball_speed'], *info['blocker']])

        # answer
        if info['ball'][1] == info['platform_2P'][1] + platform_size[1]:
            for i in range(last, idx):
                result[1].append(info['ball'][0])

            last = idx

    result[0] = result[0][:len(result[1])]

    return result

def train(side: str):
    print('------ %s ------' % side)

    x = []
    y = []

    print('Reading... ', end = '', flush = True)

    for filename in os.listdir(data_dir):
        path = os.path.join(data_dir, filename)

        if side == '1P':
            feature, ans = get_feature_and_answer_1p(path)
        else:
            feature, ans = get_feature_and_answer_2p(path)

        assert len(feature) == len(ans)

        x.extend(feature)
        y.extend(ans)

    print('Complate\nGenerating more data... ', end = '', flush = True)

    origin_len = len(x);
    for i in range(origin_len):
        if y[i] - 1 >= 0:
            x.append(x[i])
            y.append(y[i] - 1)

        if y[i] + 1 <= 200:
            x.append(x[i])
            y.append(y[i] + 1)

    print('Complete')

    d = dict()

    for i in y:
        if i not in d.keys():
            d[i] = 0
        d[i] += 1

    for i in range(201):
        if i in d.keys():
            print('%3d: %d' % (i, d[i]))
        else:
            print('%3d: 0' % i)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2)

    print('Training... ', end = '', flush = True)

    mlp = MLPClassifier(hidden_layer_sizes = (100, 100,), max_iter = 100, learning_rate_init = 0.01)

    mlp.fit(x_train, y_train)

    print('Complete')

    print(f'Training set score: {mlp.score(x_train, y_train)}')
    print(f'Test set score: {mlp.score(x_test, y_test)}')

    log_obj(mlp, 'MLP_%s.pickle' % side)


def log_obj(obj, name):
    with open(name, 'wb') as f:
        pickle.dump(obj, f)

if __name__ == '__main__':
    data_dir = '../MLGame/games/pingpong/log'
    
    train('1P')
    train('2P')
