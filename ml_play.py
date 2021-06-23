'''
The template of the script for the machine learning process in game pingpong
'''

# Import the necessary modules and classes
import os
import sys
import pickle

model_name_1p = 'DT_1P.pickle'
model_name_2p = 'DT_2P.pickle'

with open(os.path.join(os.path.dirname(__file__), model_name_1p), 'rb') as f:
    model_1p = pickle.load(f)

with open(os.path.join(os.path.dirname(__file__), model_name_2p), 'rb') as f:
    model_2p = pickle.load(f)

class MLPlay:
    def __init__(self, side):
        """
        Constructor

        @param side A string "1P" or "2P" indicates that the `MLPlay` is used by
               which side.
        """
        self.side = side
        self.ball_served = False
        self.last_blocker_pos_x = None

        if self.side == '1P':
            self.model = model_1p
        else:
            self.model = model_2p

    def update(self, scene_info):
        """
        Generate the command according to the received scene information
        """
        if scene_info['status'] != 'GAME_ALIVE':
            return 'RESET'

        if not self.ball_served:
            self.ball_served = True
            self.last_blocker_pos_x = scene_info['blocker'][0]
            return 'SERVE_TO_LEFT'

        return self.__move_to(scene_info[f'platform_{self.side}'][0] + 20, self.__predict_x(scene_info))

    def reset(self):
        """
        Reset the status
        """
        self.ball_served = False
        self.last_blocker_pos_x = None

    def __move_to(self, curr: int, pred: int) -> {0, 1, 2}:
        if pred - 3 < curr and curr < pred + 3:
            return 'NONE'
        elif curr <= pred - 3:
            return 'MOVE_RIGHT'
        else:
            return 'MOVE_LEFT'

    def __predict_x(self, scene_info) -> int:
        pred = self.model.predict([
            [*scene_info['ball'], *scene_info['ball_speed'],
                *scene_info['blocker'], scene_info['blocker'][0] - self.last_blocker_pos_x]
            ])[0]

        self.last_blocker_pos_x = scene_info['blocker'][0]

        return pred
