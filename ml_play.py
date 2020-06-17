import pprint, queue

class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0                            # speed initial
        self.car_pos = (0,0)                        # pos initial
        self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center
        pass

    def update(self, scene_info):
        # car size: (40, 80)

        if scene_info["status"] != "ALIVE":
            return "RESET"
        
        # Generate the matrix based on relative position
        grid = [[0 for i in range(5)] for j in range(5)]

        self.car_pos = scene_info[self.player]
        if len(self.car_pos) != 2:
            return 'SPEED'

        for car in scene_info['cars_info']:
            if car['id'] == self.player_no:
                continue

            ## Calculate relative position
            x = car['pos'][0] - self.car_pos[0]
            y = car['pos'][1] - self.car_pos[1]
            cmp = lambda a: 1 if a >= 0 else -1

            offset = (abs(x) // 70, abs(y) // 120)
            remain = (abs(x) %  70, abs(y) %  120)

            if max(offset[0], offset[1]) > 2:
                continue

            x_idx = 2 + cmp(x) * offset[0]
            y_idx = 2 + cmp(y) * offset[1]
            grid[y_idx][x_idx] = None

            if remain[0] and 0 <= x_idx + cmp(x) < 5:
                grid[y_idx][x_idx + cmp(x)] = None
            if remain[1] and 0 <= y_idx + cmp(y) < 5:
                grid[y_idx + cmp(y)][x_idx] = None

        pprint.pprint(grid)
        print()

        # Run BFS and get the command

        # return the command
        return "SPEED"

    def reset(self):
        """
        Reset the status
        """
        pass
