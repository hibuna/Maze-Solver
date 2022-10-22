### IMPORT MODULES

# BUILTINS

import sys, os
from pathlib import Path


# FROM FILESYSTEM

modules          = ['Image2Matrix']
for module in modules:
    code_dir        = Path(Path.cwd().parents[1])
    module_dir      = str(Path.joinpath(code_dir, module))
    sys.path.append(module_dir)

import Image2Matrix as i2m  # https://github.com/hibuna/Image2Matrix

#############################################################################


class Maze:


    def __repr__(self):
        return f"<Maze {self.width}x{self.height}, {self.width*self.height} pixels>"

    def __init__(self, maze):

        self.matrix_b   = maze
        self.width      = len(maze)
        self.height     = len(maze[0])

        self.matrix_c   = self.get_coords()

        self.start      = self.get_crd_end   # only path upper row
        self.end        = self.get_crd_start # only path bottom row

        self.junctions  = self.get_junctions()
        self.endpoints  = self.get_endpoints()
        self.nodes      = self.endpoints + self.junctions

    ### METHODS

    # COORDS

    def get_coords(self):
        # init coords for instantiating lookup tables
        coords = []
        for row in range(self.height):
            coords.append([])
            for col in range(self.width):
                coords[row].append(Maze.Coord(self, row, col, self.matrix_b[row][col]))
        return tuple(coords)


    # NODES

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
        for crd in self.coords[0]:
            if crd.path:
                return crd

    def get_crd_end(self):
        # only checks last row
        for crd in self.coords[-1]:
            if crd.path:
                return crd


    # PRINT

    def print_coords(self):
        print('\n'.join([str(coord) for coord in self.coords]))

    def print_maze(self, inverted=False):
        print(i2m.maze_print(self.matrix, inverted))


    ### DATA STRUCTURES

    class Coord:

        def __repr__(self):
            return f"<Coord {self.path}\tr{self.row}\tc{self.col} >"

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


        # RELATIVE POSITIONS (if legal else None)
        
        def N(self):
            return (self.row-1, self.col) if self.row > 0 else None #(0, self.col)

        def E(self):
            return (self.row, self.col+1) if self.col < self.width-1 else None #(self.row, self.width-1)

        def S(self):
            return (self.row+1, self.col) if self.row < self.height-1 else None #(self.height-1, self.col)
        
        def W(self):
            return (self.row, self.col-1) if self.col > 0 else None #(self.row, 0)


        # NEIGHBOURS
        
        def get_neigh_crds(self):

            coord = lambda row, col : self.maze.matrix_c[row][col]
            return [coord(neigh_pos[0], neigh_pos[1]) for neigh_pos in self.neigh_poss]
                
        def get_neigh_poss(self):
            
            # funcs to get relative row, col
            pos_funcs   = [self.N, self.E, self.S, self.W]

            is_path     = lambda pos : self.maze.matrix_b[pos[0]][pos[1]]
            return [pos_func() for pos_func in pos_funcs if pos_func() and is_path(pos_func())]


        # ROUTING

        def calc_routes(self):

            def creep(coord):

                # recursive function that creeps down a path until the next node.
                # tracks last coord as nonlocal variable to avoid creeping backwards

                nonlocal distance, last_crd
                is_node = lambda crd : crd.junction or crd.endpoint

                print(f'checking {coord}, last {last_crd}, dist {distance}')

                # got to next coord that is not self or last coord
                next_crd = None
                for crd in coord.get_neigh_crds():
                    if crd != last_crd:
                        next_crd = crd

                distance += 1

                # base case: next neighbour == node
                if is_node(next_crd):
                    return next_crd
                
                # recursion: next neighbour != node -> check neighbour's neighbour 
                else:
                    last_crd = coord
                    return creep(next_crd)


            for neigh_crd in self.get_neigh_crds():
                distance = 1
                last_crd = self
                print(f'From: {self}\tGot: {creep(neigh_crd)}\tDistance: {distance}')


if __name__=="__main__":
    assert sys.argv[1], 'Missing argument or not running through CLI'
    file = sys.argv[1]
    path = os.path.join(os.path.dirname(__file__), file)

    # generate your own maze img with: https://keesiemeijer.github.io/maze-generator/
    png  = i2m.PNG(path)
    maze = Maze(i2m.maze_matrix_walls(png, inverted=True))  # get path=True matrix

    maze.nodes[0].calc_routes()
    maze.junctions[0].calc_routes()