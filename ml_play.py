"""
The template of the main script of the machine learning process
"""

import os

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    last_ball_pos = (0, 0)
    width = 200

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        curr_ball_pos = scene_info.ball
        pf_pos = scene_info.platform
        vector = [curr_ball_pos[0] - last_ball_pos[0], curr_ball_pos[1] - last_ball_pos[1]]

        action = PlatformAction.NONE
        if vector[1] > 0:
            pred_x = curr_ball_pos[0] + vector[0] * (pf_pos[1] - curr_ball_pos[1]) / vector[1] # regardless bounding
            pred_x = int(width - abs(width - abs(pred_x) % (2 * width))) # consider bounding

            if pred_x <= pf_pos[0] + 10:
                action = PlatformAction.MOVE_LEFT
            elif pred_x >= pf_pos[0] + 30:
                action = PlatformAction.MOVE_RIGHT

        # Add randomness
        rn = os.urandom(2)
        if rn[0] % 2 == 1 and abs(pred_x - pf_pos[0] - 20) < 5:
            action = (PlatformAction.NONE, PlatformAction.MOVE_LEFT, PlatformAction.MOVE_RIGHT)[rn[1] % 3]

        last_ball_pos = curr_ball_pos

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            comm.send_instruction(scene_info.frame, action)
