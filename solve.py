import os
import sys

import image2matrix as i2m
from errors import (
    MatrixSizeError, PathCornerError, PathExitAmountError, PathExitSpacingError
)

CellType = tuple[int, int]
RowType = ColType = tuple[bool, ...]
MatrixType = tuple[RowType, ...]


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
        self.matrix = matrix

    def solve(self):
        start_cell, end_cell = self.exit_cells()
        ...

    def exit_cells(self) -> tuple[CellType, CellType]:
        cells = []
        north = self.matrix.row(0)
        east = self.matrix.col(-1)
        south = self.matrix.row(-1)
        west = self.matrix.col(0)

        for i in range(self.matrix.width):
            if north[i]:
                cells.append((0, i))
            if south[i]:
                cells.append((self.matrix.height - 1, i))

        for i in range(self.matrix.height):
            if east[i]:
                cells.append((i, self.matrix.width - 1))
            if west[i]:
                cells.append((i, 0))

        start_cell, end_cell = cells
        return start_cell, end_cell


class Validator:
    @staticmethod
    def validate(matrix: MatrixType):
        Validator.size(matrix)
        Validator.corners(matrix)
        Validator.exit_cell_amt(matrix)

        maze = Maze(Matrix(matrix))
        Validator.exit_cell_pos(*maze.exit_cells())

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
    def exit_cell_amt(matrix: MatrixType):
        north = [cell for cell in matrix[0]]
        east = [cell for cell in [row[-1] for row in matrix]]
        south = [cell for cell in matrix[-1]]
        west = [cell for cell in [row[0] for row in matrix]]
        border_cells = (*north, *east, *south, *west)
        exits = [cell for cell in border_cells if cell]
        if len(exits) != 2:
            raise PathExitAmountError("Expecting exactly 2 exits")

    @staticmethod
    def exit_cell_pos(start_cell: CellType, end_cell: CellType):
        # calc delta pos
        d_y = abs(start_cell[0] - end_cell[0])
        d_x = abs(start_cell[1] - end_cell[1])
        # if 1 space apart and on same row/col
        if d_x == 0 and d_y == 1 or d_y == 0 and d_x == 1:
            raise PathExitSpacingError("Exits must be at least 1 cell apart")


if __name__ == "__main__":
    assert sys.argv[1], 'Missing argument or not running through CLI'
    file = sys.argv[1]
    path = os.path.join(os.path.dirname(__file__), file)

    # generate your own maze img with: https://keesiemeijer.github.io/maze-generator/
    maze_path = i2m.get_maze_path(png=path)
    i2m.print_maze(matrix=maze_path)
