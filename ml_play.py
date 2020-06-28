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
        self.car_pos = (0,0)                                       # initial position
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center
        self.in_cd = 1                                             # cold down time for 'BRAKE' command
        self.vel = 0                                               # initial velocity
        pass

    def update(self, scene_info):
        # car size: (40, 80)

        if scene_info["status"] != "ALIVE":
            return "RESET"
        
        if len(scene_info[self.player]) < 2:
            return 'SPEED'

        '''
        Get basic information
        '''
        for each_car in scene_info['cars_info']:
            if each_car['id'] == self.player_no:
                self.vel = each_car['velocity']
                break
        self.car_pos = scene_info[self.player]

        '''
        Get possible move direction
        '''
        possible_dir = [[0, -1], [1, 0], [-1, 0]]
        get_dir = lambda n : -1 if n < 0 else 1
        for each_car in scene_info['cars_info']:
            if each_car['id'] == self.player_no: # ignore me
                continue
            if each_car['pos'][1] > self.car_pos[1]: # ignore the cars that behind me
                continue

            x_distance = each_car['pos'][0] - self.car_pos[0] # x distance between each car and me
            y_distance = each_car['pos'][1] - self.car_pos[1] # y distance between each car and me

            '''
            left and right
            '''
            if abs(x_distance) < 90 and abs(y_distance) < 80: # too close
                try:
                    possible_dir.remove([get_dir(x_distance), 0])
                except:
                    pass

            '''
            forward
            '''
            if abs(x_distance) < 45 and abs(y_distance) < 160 and each_car['velocity'] < self.vel:
                try:
                    possible_dir.remove([0, -1])
                except:
                    pass

        '''
        Determine commands to be executed
        '''
        command = []

        self.in_cd -= 1
        if [0, -1] in possible_dir:
            command.append('SPEED')
        else:
            if [-1, 0] in possible_dir and self.car_pos[0] > 25:
                command.append('MOVE_LEFT')
            elif [1, 0] in possible_dir and self.car_pos[0] < 605:
                command.append('MOVE_RIGHT')

            if not self.in_cd:
                command.append('BRAKE')
                self.in_cd = 3

        return command

    def reset(self):
        """
        Reset the status
        """
        pass
