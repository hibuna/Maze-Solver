import copy
import sys
from pathlib import Path

# import modules from master code dir
# https://github.com/WillyKeurig/Image2Matrix
modules          = ['Image2Matrix']
for module in modules:
    code_dir        = Path(Path.cwd().parents[1])
    module_dir      = str(Path.joinpath(code_dir, module))
    sys.path.append(module_dir)

#############################################################################

import Image2Matrix.main as i2m


class Maze:


    def __repr__(self):
        return f"<Maze {self.width}x{self.height}, {self.width*self.height} pixels>"

    def __init__(self, maze):

        self.matrix   = maze
        self.width    = len(maze)
        self.height   = len(maze[0])
        self.coords   = self.get_coords()

        # lookup table matrix of per row or col - r=row, w=wall, p=path
        self.lookup_r, self.lookup_rw, self.lookup_rp = self.lookup_rows()
        self.lookup_r, self.lookup_cw, self.lookup_cp = self.lookup_cols()

        self.start    = self.lookup_rp[0]  # only path upper row
        self.end      = self.lookup_rp[-1] # only path bottom row

    ### METHODS

    # COORDS

    def get_coords(self):
        coords = []
        w = len(self.matrix)
        h = len(self.matrix[0])

        for row in range(w):
            for col in range(h):
                coords.append(Maze.Coord(row, col, self.matrix[row][col]))
        
        return coords

    def get_coord_start(self):  # only looks in top row
        for i in range(self.width):
            if not self.matrix[0][i]:
                return Maze.Coord(0, i)

    def get_coord_end(self):  # only looks in bottom row
        for i in range(self.width):
            if not self.matrix[-1][i]:
                return Maze.Coord(0, i)

    def get_row(self, row): 
        return list([coord for coord in self.coords if coord.row == row])

    def get_col(self, col):
        return list([coord for coord in self.coords if coord.col == col])


    # LOOKUP TABLE GEN

    def lookup_rows(self):

        # create list if rows
        rows = []
        for i in range(self.height):
            rows.append(self.get_row(i))

        # copy ptr array[coords]
        walls = []
        paths = []

        for row in rows:
            walls.append(copy.copy(row))
            paths.append(copy.copy(row))

        for row in range(self.height):
            for cell in reversed(range(self.width)):
                if self.matrix[row][cell]:
                    paths[row].pop(cell)  # remove ptr to wall Coord
                else:
                    walls[row].pop(cell)  # remove ptr to path Coord

        return rows, walls, paths

    def lookup_cols(self):

        # create list if rows
        cols = []
        for i in range(self.width):
            cols.append(self.get_col(i))

        # copy pointer array[coords]
        walls = []
        paths = []

        for col in cols:
            walls.append(copy.copy(col))
            paths.append(copy.copy(col))

        for col in reversed(range(self.width)):
            for cell in reversed(range(self.height)):
                if self.matrix[col][cell]:
                    paths[col].pop(cell)  # remove ptr to wall
                else:
                    walls[col].pop(cell)  # remove ptr to path

        return cols, walls, paths


    # PRINT

    def print_coords(self):
        print('\n'.join([str(coord) for coord in self.coords]))

    def print_maze(self):
        print(i2m.maze_print(self.matrix))


    ### DATA STRUCTURES

    class Coord:

        def __repr__(self):
            return f"<Coord {self.wall}\tr{self.row}\tc{self.col} >"

        def __init__(self, row, col, wall=False):
            self.row    = row
            self.col    = col
            self.wall   = wall



if __name__=="__main__":
    assert sys.argv[1], 'Missing argument or not running through CLI'
    path = sys.argv[1]
    png  = i2m.PNG(path)
    maze = Maze(i2m.maze_matrix_walls(png))
    