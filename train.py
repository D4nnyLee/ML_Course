#!/usr/bin/env python3

import os
import pickle

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def log_obj(obj, name):
    with open(name, 'wb') as f:
        pickle.dump(obj, f)

def collide_with(side: str, scene_info) -> bool:
    ball_size = (5, 5)
    platform_size = (40, 30)

    if side == '1P' and scene_info['ball'][1] + ball_size[1] == scene_info['platform_1P'][1]:
        return True
    if side == '2P' and scene_info['platform_2P'][1] + platform_size[1] == scene_info['ball'][1]:
        return True
    return False

def train(side: str):
    data_dir = '../MLGame/games/pingpong/log'

    x = []
    y = []

    for filename in os.listdir(data_dir):
        f = open(os.path.join(data_dir, filename), 'rb')
        all_scene_info = pickle.load(f)
        f.close()

        last_blocker_x = 85
        last_frame = 0
        tmp = [[], []]

        for scene_info in all_scene_info:
            tmp[0].append([*scene_info['ball'], *scene_info['ball_speed'], *scene_info['blocker'], last_blocker_x - scene_info['blocker'][0]])
            last_blocker_x = scene_info['blocker'][0]

            if collide_with(side, scene_info):
                for _ in range(last_frame, scene_info['frame']):
                    tmp[1].append(scene_info['ball'][0])
                last_frame = scene_info['frame']

        x.extend(tmp[0][:len(tmp[1])])
        y.extend(tmp[1])

    '''
    orig_len = len(x)
    for i in range(orig_len):
        if y[i] - 1 >= 0:
            x.append(x[i])
            y.append(y[i] - 1)
        if y[i] + 1 <= 200:
            x.append(x[i])
            y.append(y[i] + 1)
    '''

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = .2)

    knn = KNeighborsClassifier(2)

    knn.fit(x_train, y_train)

    y_pred = knn.predict(x_test)

    print('Accuracy score: %2d%%' % (accuracy_score(y_test, y_pred) * 100))

    log_obj(knn, 'KNN_%s.pickle' % side)

if __name__ == '__main__':
    # train('1P')
    train('2P')
