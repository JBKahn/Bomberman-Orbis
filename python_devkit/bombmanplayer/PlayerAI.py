#Player.py ai
import random

from bombmanclient.Client import *
from copy import copy
from Enums import *
from Direction import *
from Queue import Queue


class PlayerAI():

    def __init__(self):
        self.blocks = []

    def new_game(self, map_list, blocks_list, bombers, player_index):
        '''
        Called when a new game starts.
        
        map_list: a list of lists that describes the map at the start of the game

            e.g.
                map_list[1][2] would return the MapItem occupying position (1, 2)

        blocks_list: a list of tuples which indicates a block occupies the position indicated by the tuple

            e.g.
                if (2, 1) is in blocks_list then map_list[2][1] = MapItems.BLOCK

        bombers: a dictionary of dictionaries which contains the starting positions, bomb range and bombs available for both players. 
            use with player_index to find out information about the bomber. 
            
            key: an integer for player_index
            value: {'position': x, y coordinates of the bomber's position, 'bomb_range': bomb range, 'bomb_count': the number of bombs you have available }

            e.g.
                bombers[1]['bomb_range'] will give you the bomb range of a bomb if player 2 is to place a bomb in this turn. 

        player_index: yor player index.
            bombers[player_index][0] returns your starting position

        '''
        self.blocks = blocks_list[:]

    def get_move(self, map_list, bombs, powerups, bombers, explosion_list, player_index, move_number):
        '''
        Called when a move is requested by the game server

        Returns a string which represents the action that the Bomber should carry out in this turn. 
        Defaults to STAY_PUT if a string value that is not associated with a move/bomb move action is passed back. 

        Args: 
            map_list: a list of lists that describes the current map
                map_list[0][0] would return the MapItem occupying position (0, 0)
            
            bombs: a dictionary that contains information of bombs currently on the map. 
                key: a tuple of the bomb's location
                value: a dictionary with keys 'owner', 'range', 'time_left'

                e.g.
                    bombs[(13, 5)]['owner'] will return the index of the Bomber who owns the bomb at (13, 5)

                No bombs with time_left = 0 will appear in this list.

            powerups: a dictionary that contains the power-ups currently on the map. 
                key: a tuple of the power-up's location
                value: a string which represents the type of power-up ('FIREUP' or 'BOMBUP').

                e.g.
                    if powerups[(2, 3)] == 'FIREUP' then there is a FIREUP in position (2, 3)
            
            bombers: a dictionary that contains the player's current stats. 
                key: player index (0 or 1)
                value: a dictionay with ktime_lefteys 'position', 'bomb_range' and 'bomb_count'

                e.g.
                    bombers[0]['bomb_range'] will return player 1's current bomb range. 

            explosion_list: a list of tuples that denotes the position of tiles which are currently exploding.

                By the next get_move call, all currently exploding tiles not be exploding. 
                However, in the next turn, another bomb may cause some of the same tiles to explode. 
            
            player_index: an integer representing your player index.
                bombers[player_index] returns the dictionary containing stats about your bomber
            
            move_number: the current turn number. Use to deterimine if you have missed turns. 
        '''

        next_world =[]
        for y in range(16):
           for x in range(y,16):
               map_list[x][y], map_list[y][x] = map_list[y][x], map_list[x][y]



        bombMove = False
        my_position = bombers[player_index]['position']

        # updating the list of blocks
        for explosion in explosion_list:
            print explosion_list
            if explosion in self.blocks: 
                self.blocks.remove(explosion)
        
        #sorted_bombs = sorted(copy(bombs), key=lambda bomb: bombs[bomb]['time_left']) 


        for i in range(1,17):
            next_world.append(self.next_world((next_world and next_world[-1]) or map_list, bombs,i))

        (depth,direction) = self.find_path(next_world, my_position,'',0)
        move = direction



        # if (next_world[0][my_position[1]][my_position[0]] == 'EXPLOSIION'):
        #     run = 1; 


        # validmoves = []
        # neighbour_blocks = []
        # for move in Directions.values():
        #     x = my_position[0] + move.dx
        #     y = my_position[1] + move.dy

        #     # Checks to see if neighbours are walkable, and stores the neighbours which are blocks
        #     if map_list[y][x] in [Enums.MapItems.BLANK, Enums.MapItems.POWERUP] and next_world[0][y][x] != 'EXPLOSIION':
        #         # walkablebombers is a list in enums.py which indicates what type of tiles are walkable
        #         # if next_world[x][y] == ''
        #         validmoves.append(move)
        #     elif next_world[0][y][x] == 'BLOCK': 
        #         neighbour_blocks.append((y, x))

        # if len(neighbour_blocks) > 0:
        #     bombMove = True


        transform = {'BLOCK':'b', 'WALL':'w', 'BLANK': ' ', 'POWERUP': 'P', 'EXPLOSION': 'x', 'BOMB': 'O'}
        print 'next map is:'
        for i in next_world[5]:
            print ''.join([transform.get(spot,spot) for spot in i])
        print 'this map is:'
        for i in map_list:
            print ''.join([transform.get(spot,spot) for spot in i])

        print bombs

        # there's no where to move to
        # if len(validmoves) == 0: 
        #     return Directions['still'].action

        # # can move somewhere, so choose a tile randomly
        # move = validmoves[random.randrange(0, len(validmoves))]


        # if bombMove: 
        #     return move.bombaction
        # else: 
        return move.action

    def path_exists(start, end, map_list):
        ''' 
        Takes two tuples that represents the starting, ending point and the currenet map to determine if a path between the two points exists on the map. 

        returns True if there is a path with no blocks, bombs or walls in it's path between start and end. 
        returns False otherwise. 

        Args: 
            start: a tuple which correspond to the starting point of the paths
            end: a tuple which correspond to the ending point of the path.
        '''
        open_list = [start]
        visited = []

        while len(open_list) != 0:
            current = open_list.pop(0)

            for direction in Directions.values():
                x = current[0] + direction.dx
                y = current[1] + direction.dy

                if (x, y) == end: 
                    return True

                if (x, y) in visited: 
                    continue

                if map_list[x][y] in walkable: 
                    open_list.append((x, y))

                visited.append((x, y))

        return False

    def manhattan_distance(start, end):
        '''
        Returns the Manhattan distance between two points. 

        Args:
            start: a tuple that represents the coordinates of the start position. 
            end: a tuple that represents the coordinates of the end postion
        '''
        return (abs(start[0]-end[0])+abs(start[1]-end[1]))


    def next_world(self, map_list, bombs,depth):
        '''
        Returns a the map with all tiles updated exceot for the opponents movement.  

        Args:
            see  get_move
        '''
        map_stuff = {'BLOCK':'BLOCK', 'BLANK':'BLANK', 'EXPLOSION':'EXPLOSION', 'BOMB':'BOMB','POWERUP':'POWERUP', 'WALL':'WALL'}
        world = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        for index,row in enumerate(map_list):
            for item in row:
                world[index].append(map_stuff[item])

        for y in range(16):
           for x in range(16):
               if world[x][y] == 'EXPLOSION':
                   world[x][y] = 'BLANK'

        bomb_queue = Queue()
        for position, bomb in bombs.iteritems():
            if (bomb['time_left'] == depth):

                bomb_queue.put([position, bomb])
        while not bomb_queue.empty():
            current_bomb = bomb_queue.get(False)
            bomb = current_bomb[1]
            position = current_bomb[0]
            if world[position[1]][position[0]] != 'BOMB':
                continue
            world[position[1]][position[0]] = 'EXPLOSION'


            for direction in [[1, 0], [0, 1], [-1, 0], [0, -1]]:
                dx = direction[0]
                dy = direction[1]
                for i in range(1,bomb['range']+1):
                    new_y = position[0] + dx*i
                    new_x = position[1] + dy*i
                    old_item = world[new_x][new_y]
                    if old_item in ('BLANK', 'POWERUP', 'BLOCK', 'WALL'):
                        if old_item == 'WALL':
                            break
                        world[new_x][new_y] = 'EXPLOSION'
                        if old_item == 'BLOCK':
                            break
                    if old_item == 'BOMB':
                        if bombs.get((new_y, new_x)):
                            bomb_queue.put([(new_y, new_x), bombs[(new_y, new_x)]])
                            bombs[(new_y, new_x)]['time_left']= min (bombs[(new_y, new_x)]['time_left'],bomb['time_left'])

                    if old_item == 'PLAYER':
                        # make_safe()
                        pass
                    if old_item is not 'BOMB':
                        world[new_x][new_y] = 'EXPLOSION'
        return world



    def find_path (self, next_world, position,direction,depth):
        result = [];
        x = position[1]
        y = position[0]
        if direction:
            x += direction.dx
            y += direction.dy	
        if (next_world[depth][x][y] not in ['BLANK','POWERUP']):
            return (depth,direction)
        elif depth == 5:
            return (depth, direction)
        return max([(self.find_path(next_world, (y,x), direction,depth+1),direction) for direction in Directions.values()],key=lambda x: x[0])
                    

        # '''
        # depth += 1

        # will i die in this spot at this time? 
        #     return death, path, depth  

        # if (depth == 10)
        #     return (depth,path)

        #      find max return depth for recursive left down and right and stay: 
        #      and return that
       
