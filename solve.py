### IMPORT

# region    IMPORT > BUILTINS
import sys, os
from pathlib import Path

# endregion

# region    IMPORT > FILESYSTEM

modules          = ['Image2Matrix']
for module in modules:
    code_dir        = Path(Path.cwd().parents[1])
    module_dir      = str(Path.joinpath(code_dir, module))
    sys.path.append(module_dir)

import Image2Matrix as i2m  # https://github.com/hibuna/Image2Matrix

# endregion

#############################################################################

### COMMENTS

# LARGE MAZE EXITS WITHOUT EXCEPTION AT RECURSION DEPTH 2123.
# Will branch to implement tail-recursion optimization



class Maze:


    def __repr__(self):
        return f"<Maze {self.width}x{self.height}, {self.width*self.height} pixels>"

    def __init__(self, maze):

        self.matrix_b   = maze

        # testing purposes, multiple routes (maze.png):
        # self.matrix_b[2][3] = True
        # self.matrix_b[4][3] = True

        self.width      = len(maze[0])
        self.height     = len(maze)

        self.matrix_c   = self.get_coords()
        self.instantiate_coords()  # populate Coord attributes depending on other initialized Coords

        self.start      = self.get_crd_start()  # only path upper row
        self.end        = self.get_crd_end()    # only path bottom row

        self.junctions  = self.get_junctions()
        self.endpoints  = self.get_endpoints()
        self.nodes      = self.endpoints + self.junctions


    ### METHODS

    # region    METHODS > COORDS

    def get_coords(self):
        # init coords for instantiating lookup tables
        coords = []
        for row in range(self.height):
            coords.append([])
            for col in range(self.width):
                coords[row].append(Maze.Coord(self, row, col, self.matrix_b[row][col]))
        return tuple(coords)

    def instantiate_coords(self):
        for row in self.matrix_c:
            for crd in row:
                crd.instantiate()

    # endregion

    # region    METHODS > NODES 

    def get_junctions(self):
        junctions = []
        for row in self.matrix_c:
            for crd in row:
                if crd.junction:
                    junctions.append(crd)
        return tuple(junctions)

    def get_endpoints(self):
        endpoints = []
        for row in self.matrix_c:
            for crd in row:
                if crd.endpoint:
                    endpoints.append(crd)
        return tuple(endpoints)

    def get_crd_start(self):
        # only checks first
        for crd in self.matrix_c[0]:
            if crd.path:
                return crd

    def get_crd_end(self):
        # only checks last row
        for crd in self.matrix_c[-1]:
            if crd.path:
                return crd

    #endregion

    # region    METHODS > PRINT 

    def print_coords(self):
        print('\n'.join([str(coord) for coord in self.coords]))

    def print_maze(self, inverted=False):
        print(i2m.maze_print(self.matrix_b, inverted))

    # endregion


    ### DATA STRUCTURES

    class Coord:

        def __repr__(self):
            return f"<Coord\t{self.path}\tr{self.row}\tc{self.col} >"

        def __init__(self, maze, row, col, path=False):

            # maze (outer class)
            self.maze           = maze
            self.height         = maze.height
            self.width          = maze.width

            # coord pos
            self.row            = row                # 0:height-1
            self.col            = col                # 0:width-1

            # coord data
            self.path           = path
            self.neigh_poss     = self.get_neigh_poss()
            # self.neigh_objs     = self.get_neigh_objs()
            self.endpoint       = self.path and len(self.neigh_poss) == 1
            self.junction       = self.path and len(self.neigh_poss) > 2

            self.via            = None
            self.distance       = -1
            self.finished       = False

            # self.nodes_adj      = self.get_nodes_adj()

        def instantiate(self):
            self.neigh_crds 	= self.get_neigh_crds()
            self.nodes_connected= self.get_nodes_connected()

        # region    RELATIVE POSITIONS
        # (if legal else None)
        
        def N(self):
            return (self.row-1, self.col) if self.row > 0 else None #(0, self.col)

        def E(self):
            return (self.row, self.col+1) if self.col < self.width-1 else None #(self.row, self.width-1)

        def S(self):
            return (self.row+1, self.col) if self.row < self.height-1 else None #(self.height-1, self.col)
        
        def W(self):
            return (self.row, self.col-1) if self.col > 0 else None #(self.row, 0)

        # endregion

        # region    NEIGHBOURS
        
        def get_neigh_crds(self):

            coord = lambda row, col : self.maze.matrix_c[row][col]
            return [coord(neigh_pos[0], neigh_pos[1]) for neigh_pos in self.neigh_poss]
                
        def get_neigh_poss(self):
            
            is_path     = lambda pos : self.maze.matrix_b[pos[0]][pos[1]]

            # funcs to get relative row, col
            pos_fcs     = [self.N, self.E, self.S, self.W]
            neigh_poss  = []

            for pos_fc in pos_fcs:
                pos = pos_fc()  # relative position

                if pos and is_path(pos):
                    neigh_poss.append(pos)

            return neigh_poss

        # endregion

        # region    ROUTES

        def get_nodes_connected(self):

            def creep_until_node(distance, coord, last_crd):

                # recursive function that creeps down a path until the next node.
                # tracks last coord as nonlocal variable to avoid creeping backwards

                distance += 1

                # got to neigh coord that is not last coord
                # this prevents creeping backwards
                next_crd = None
                for crd in coord.get_neigh_crds():
                    if crd != last_crd:
                        next_crd = crd

                # base case: next neighbour == node
                if next_crd.junction or next_crd.endpoint:
                    return distance, next_crd
                
                # recursion: next neighbour != node -> check neighbour's neighbour 
                else:
                    return creep_until_node(distance, next_crd, coord)

            nodes = []

            for neigh_crd in self.get_neigh_crds():

                # skip when neighbour coord is out of matrix bounds
                if neigh_crd == None:
                    continue

                # if direct neighbour is node, append node at distance 1
                elif neigh_crd.junction or neigh_crd.endpoint:
                    nodes.append((1, neigh_crd))

                # creep down path until node
                else:
                    next_node = creep_until_node(1, neigh_crd, self)
                    nodes.append((next_node[0], next_node[1]))
                    
            return nodes

        # endregion


### PROGRAM

if __name__=="__main__":

    sys.setrecursionlimit(2123)

    assert sys.argv[1], 'Missing argument or not running through CLI'
    file = sys.argv[1]
    path = os.path.join(os.path.dirname(__file__), file)

    # generate your own maze img with: https://keesiemeijer.github.io/maze-generator/
    png  = i2m.PNG(path)
    maze = Maze(i2m.maze_matrix_walls(png, inverted=True))  # get path=True matrix

    routes = []

    start = maze.start

    def calc_nodes_branching_from_node(start, end):

        def first_in_Q():
            # for q in sorted(queue, key=lambda x: x.distance):
                # print(q.distance, q)
            for node in sorted(queue, key=lambda x: x.distance):
                if node.distance != -1:
                    # print('\n', node)
                    return node

        def process(node):

            nonlocal recur
            recur += 1
            print(recur)

            # base case: all nodes processed
            if not queue:
                return

            queue.remove(node)

            # print(f'_____\n{node} via \n{node.via} {node.distance}')

            for connected in node.nodes_connected:

                dst = connected[0]
                crd = connected[1]

                # print(f'\tadjacent node {crd} at {dst}')
                # print(f'\t\t{crd.distance} via {crd.via}')

                # skip if finished
                if crd not in queue:
                    # print('\t\tskipped\n')
                    continue

                # distance not set or longer than current route, set distance and via
                if crd.distance == -1 or crd.distance > dst + node.distance:
                    # print(f'\t\tsetting distance from {crd.distance} to {dst} + {node.via.distance}\n\t\tsetting via from {crd.via} to {node}\n')
                    crd.distance = dst + node.distance
                    crd.via = node

            process(first_in_Q())

        queue           = list(maze.nodes)
        print(len(queue))

        # init starting node
        start.distance  = 0
        start.via       = start

        recur = 0

        process(first_in_Q())

        node = end
        route = []

        while node != start:
            route.append((node.distance, node.via, node))
            node = node.via

        with open('route.txt', 'w') as f:
            for x in reversed(route):
                print(x)
                f.write(str(x))

    calc_nodes_branching_from_node(maze.start, maze.end)
