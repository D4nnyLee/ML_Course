#!python3

import os
import pickle

import numpy as np

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def log_obj(obj, name):
    with open(name, 'wb') as f:
        pickle.dump(obj, f)

def hash_list(l: list):
    assert len(l) == 7

    bit_len = 10
    ret = 0
    for i in range(7):
        val = l[i] + 2 ** (bit_len - 1)

        assert 0 <= val and val < 2 ** bit_len
        ret <<= bit_len
        ret |= val
    return ret

def collide(side, scene_info) -> bool:
    if side == '1P' and scene_info['ball'][1] >= 415:
        return True
    if side == '2P' and scene_info['ball'][1] <= 80:
        return True
    return False

def train(side: str):
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'log')

    fd = None

    '''
    Prepare dataset
    '''
    print('start preparing dataset...')
    x, y = [], []
    in_x = set()
    for filename in os.listdir(data_dir):
        with open(os.path.join(data_dir, filename), 'rb') as f:
            data = pickle.load(f)
            assert data['ml_1P']['scene_info'] == data['ml_2P']['scene_info']
            scene_info = data[f'ml_{side}']['scene_info']

        length = len(scene_info)

        '''
        Convert scene_info to features
        '''
        last_blocker_x = scene_info[0]['blocker'][0]

        features = []
        for info in scene_info:
            curr_blocker_x = info['blocker'][0]

            features.append([*info['ball'], *info['ball_speed'],
                *info['blocker'], curr_blocker_x - last_blocker_x])

            last_blocker_x = curr_blocker_x

        assert len(features) == length

        '''
        Create label
        '''
        pending = []
        for i in range(length):
            if collide(side, scene_info[i]):
                for p in pending:
                    hash_val = hash_list(p)

                    if hash_val in in_x:
                        continue

                    x.append(p)
                    y.append(scene_info[i]['ball'][0] + 2) # x coordinate of the middle of the ball
                    in_x.add(hash_val)

                pending.clear()
            else:
                pending.append(features[i])

    assert len(x) == len(y)
    assert len(x) == len(in_x)
    print('done')

    x = np.array(x)
    y = np.array(y)

    print(x.shape)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = .2)

    '''
    Create model
    '''
    clf = DecisionTreeClassifier(random_state = 0)
    print('start training...')
    clf.fit(x_train, y_train)
    print('done')

    y_pred = clf.predict(x_test)

    print(f'accuracy_score: {accuracy_score(y_test, y_pred) * 100}%')

    log_obj(clf, f'DT_{side}.pickle')

if __name__ == '__main__':
    train('1P')
    train('2P')
