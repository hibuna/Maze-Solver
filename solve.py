import enum
import os
import sys

import image2matrix as i2m
from errors import (
    MatrixSizeError,
    PathCornerError,
    PathExitAmountError,
    PathExitSpacingError,
)

CellType = dict
RowType = ColType = tuple[bool, ...]
MatrixType = tuple[RowType, ...]


class WindRose(enum.Enum):
    N = -1, 0
    E = 0, 1
    S = 1, 0
    W = 0, -1


class Matrix:
    def __init__(self, matrix: MatrixType):
        self.matrix = matrix
        self.width = len(matrix[0])
        self.height = len(matrix)

    def row(self, index: int) -> RowType:
        i = index if index >= 0 else (index * -1) - 1  # equalize negative index
        if i >= self.height:
            raise IndexError(f"Index out of bounds: {index}")
        return self.matrix[index]

    def col(self, index: int) -> ColType:
        i = index if index >= 0 else (index * -1) - 1  # equalize negative index
        if i >= self.width:
            raise IndexError(f"Index out of bounds: {index}")
        return tuple([row[index] for row in self.matrix])


class Maze:
    def __init__(self, matrix: Matrix):
        self.mx = matrix

    WALL = False
    PATH = True

    def solve(self):
        # start and end have ["previous"] == {}
        node_start, node_end = self.exit_nodes()
        ...

    def exit_nodes(self) -> tuple[dict, dict]:
        nodes = []
        north_border = self.mx.row(0)
        east_border = self.mx.col(-1)
        south_border = self.mx.row(-1)
        west_border = self.mx.col(0)

        for i in range(self.mx.width):
            if north_border[i] is Maze.PATH:
                nodes.append((0, i))
            if south_border[i] is Maze.PATH:
                nodes.append((self.mx.height - 1, i))

        for i in range(self.mx.height):
            if east_border[i] is Maze.PATH:
                nodes.append((i, self.mx.width - 1))
            if west_border[i] is Maze.PATH:
                nodes.append((i, 0))

        start, end = nodes
        start = self.create_node(row=start[0], col=start[1], previous={})
        end = self.create_node(row=end[0], col=end[1], previous={})
        return start, end

    @staticmethod
    def create_node(
        row: int,
        col: int,
        previous: dict,
        north: bool = False,
        east: bool = False,
        south: bool = False,
        west: bool = False,
    ):
        return {
            "row": row,
            "col": col,
            "previous": previous,
            "north": north,
            "east": east,
            "south": south,
            "west": west,
        }

    def creep(self, row: int, col: int, direction: WindRose):
        """Creep from a point until you hit a wall. Return row, col of cell before wall."""
        # creep until out of bounds or hitting wall
        d_row, d_col = direction.value  # delta row/col
        while True:
            row += d_row
            col += d_col
            out_of_bounds = (
                row < 0,
                row >= self.mx.height,
                col < 0,
                col >= self.mx.width,
            )
            if any(out_of_bounds):
                break
            next_cell = self.mx.matrix[row][col]
            if next_cell is Maze.WALL:
                break

        # return previous cell after hitting wall
        row -= d_row
        col -= d_col
        return row, col


class Validator:
    @staticmethod
    def validate(matrix: MatrixType):
        Validator.size(matrix)
        Validator.corners(matrix)
        Validator.exit_amt(matrix)

        maze = Maze(Matrix(matrix))
        Validator.exit_pos(*maze.exit_nodes())

    @staticmethod
    def size(matrix: MatrixType):
        if len(matrix) < 3 or any(len(row) < 3 for row in matrix):
            raise MatrixSizeError("Matrix must be at least 3x3")

    @staticmethod
    def corners(matrix: MatrixType):
        corners = [
            matrix[0][0],
            matrix[0][-1],
            matrix[-1][0],
            matrix[-1][-1],
        ]
        if any(corners):
            raise PathCornerError("Corner cannot be path")

    @staticmethod
    def exit_amt(matrix: MatrixType):
        matrix = Matrix(matrix)
        border_cells = (
            *[cell for cell in matrix.row(0)],  # North
            *[cell for cell in matrix.col(-1)],  # East
            *[cell for cell in matrix.row(-1)],  # South
            *[cell for cell in matrix.col(0)],  # West
        )
        exits = [cell for cell in border_cells if cell]
        if len(exits) != 2:
            raise PathExitAmountError("Expecting exactly 2 exits")

    @staticmethod
    def exit_pos(node_start: dict, node_end: dict):
        # calc delta pos
        d_y = abs(node_start["row"] - node_end["row"])
        d_x = abs(node_start["col"] - node_end["col"])
        # if 1 space apart and on same row/col
        if d_x == 0 and d_y == 1 or d_y == 0 and d_x == 1:
            raise PathExitSpacingError("Exits must be at least 1 cell apart")


if __name__ == "__main__":
    assert sys.argv[1], "Missing argument or not running through CLI"
    file = sys.argv[1]
    path = os.path.join(os.path.dirname(__file__), file)

    # generate your own maze img with: https://keesiemeijer.github.io/maze-generator/
    maze_path = i2m.get_maze_path(png=path)
    i2m.print_maze(matrix=maze_path)
