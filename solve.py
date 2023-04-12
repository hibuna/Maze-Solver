import os
import sys

import image2matrix as i2m
from errors import (
    PathExitError,
    MatrixSizeError,
    PathCornerError,
)

Cell = tuple[int, int]
Row = Col = tuple[bool, ...]
Matrix = tuple[Row, ...]


class Maze:
    def __init__(self, matrix: Matrix) -> None:
        self.validate_matrix(matrix)

        self.matrix = matrix
        self.width = len(matrix[0])
        self.height = len(matrix)

    def row(self, index: int) -> Row:
        i = index if index >= 0 else (index * -1) - 1  # equalize negative index
        if i >= self.height:
            raise IndexError(f"Index out of bounds: {index}")
        return self.matrix[i]

    def col(self, index: int) -> Col:
        i = index if index >= 0 else (index * -1) - 1  # equalize negative index
        if i >= self.width:
            raise IndexError(f"Index out of bounds: {index}")
        return tuple([row[i] for row in self.matrix])

    def start_cell(self) -> Cell:
        for cell in self.row(0):
            if cell:
                return 0, self.row(0).index(cell)

        for cell in self.col(0):
            if cell:
                return self.col(0).index(cell), 0

        raise PathExitError("No path found in first row or first col")

    def end_cell(self) -> Cell:
        for cell in self.row(-1):
            if cell:
                return len(self.matrix), self.row(-1).index(cell)

        for cell in self.col(-1):
            if cell:
                return self.col(-1).index(cell), len(self.matrix[0])

        raise PathExitError("No path found in last row or last col")

    @staticmethod
    def validate_matrix(matrix: Matrix) -> None:
        if len(matrix) < 3 or any(len(row) < 3 for row in matrix):
            raise MatrixSizeError("Matrix must be at least 3x3")

        corners = [
            matrix[0][0],
            matrix[0][-1],
            matrix[-1][0],
            matrix[-1][-1],
        ]
        if any(corners):
            raise PathCornerError("Corner cannot be path")

        north = [cell for cell in matrix[0]]
        east = [cell for cell in [row[-1] for row in matrix]]
        south = [cell for cell in matrix[-1]]
        west = [cell for cell in [row[0] for row in matrix]]
        border_cells = (*north, *east, *south, *west)
        exits = [cell for cell in border_cells if cell]
        if len(exits) != 2:
            raise PathExitError("Expecting exactly 2 exits")


if __name__ == "__main__":
    assert sys.argv[1], 'Missing argument or not running through CLI'
    file = sys.argv[1]
    path = os.path.join(os.path.dirname(__file__), file)

    # generate your own maze img with: https://keesiemeijer.github.io/maze-generator/
    maze_path = i2m.get_maze_path(png=path)
    i2m.print_maze(matrix=maze_path)

    maze = Maze(matrix=maze_path)
    print(maze.start_cell())
    print(maze.end_cell())
