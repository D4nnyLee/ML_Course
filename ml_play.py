'''
The template of the script for the machine learning process in game pingpong
'''

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import pickle
import os

model_name_1p = 'MLP_1P.pickle'
model_name_2p = 'MLP_2P.pickle'

with open(os.path.join(os.path.dirname(__file__), model_name_1p), 'rb') as f:
    mlp_1p = pickle.load(f)

with open(os.path.join(os.path.dirname(__file__), model_name_2p), 'rb') as f:
    mlp_2p = pickle.load(f)

def ml_loop(side: str):
    '''
    The main loop for the machine learning process

    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == '1P':
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```

    @param side The side which this script is executed for. Either '1P' or '2P'.
    '''

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    last_blocker_pos = (85, 240)

    def move_to(curr: int, pred: int) -> {0, 1, 2}:
        if pred - 3 < curr and curr < pred + 3:
            return 0 # NONE
        elif curr <= pred - 3:
            return 1 # Right
        else:
            return 2 # Left

    def predict_x(mlp) -> int:
        nonlocal last_blocker_pos
        curr_blocker_pos = scene_info['blocker']
        
        blocker_speed = (last_blocker_pos[0] - curr_blocker_pos[0], last_blocker_pos[1] - curr_blocker_pos[1])

        dest = mlp.predict([[*scene_info['ball'], *scene_info['ball_speed'], *curr_blocker_pos, *blocker_speed]])[0]

        last_blocker_pos = curr_blocker_pos

        return dest

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info['status'] != 'GAME_ALIVE':
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({'frame': scene_info['frame'], 'command': 'SERVE_TO_LEFT'})
            ball_served = True
        else:
            if side == '1P':
                command = move_to(scene_info['platform_1P'][0] + 20, predict_x(mlp_1p))
            else:
                command = move_to(scene_info['platform_2P'][0] + 20, predict_x(mlp_2p))

            comm.send_to_game({'frame': scene_info['frame'], 'command': ['NONE', 'MOVE_RIGHT', 'MOVE_LEFT'][command]})
