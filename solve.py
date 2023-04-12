import os
import sys

import image2matrix as i2m

Cell = tuple[int, int]
Row = Col = tuple[bool, ...]
Matrix = tuple[Row]


class Maze:
    def __init__(self, matrix: Matrix) -> None:
        self.matrix = matrix
        self.width = len(matrix[0])
        self.height = len(matrix)

    def row(self, index: int) -> Row:
        i = index if index >= 0 else (index * -1) - 1  # equalize negative index
        if i >= self.height:
            raise Exception(f"Index out of bounds: {index}")
        return self.matrix[i]

    def col(self, index: int) -> Col:
        i = index if index >= 0 else (index * -1) - 1  # equalize negative index
        if i >= self.width:
            raise Exception(f"Index out of bounds: {index}")
        return tuple([row[i] for row in self.matrix])

    def start_cell(self) -> Cell:
        for cell in self.row(0):
            if cell:
                return 0, self.row(0).index(cell)

        for cell in self.col(0):
            if cell:
                return self.col(0).index(cell), 0

        raise Exception("No path found in first row or first col")

    def end_cell(self) -> Cell:
        for cell in self.row(-1):
            if cell:
                return len(self.matrix), self.row(-1).index(cell)

        for cell in self.col(-1):
            if cell:
                return self.col(-1).index(cell), len(self.matrix[0])

        raise Exception("No path found in last row or last col")

    def check_borders_valid(self) -> None:
        corners = [
            self.matrix[0][0],
            self.matrix[0][-1],
            self.matrix[-1][0],
            self.matrix[-1][-1],
        ]
        if any(corners):
            raise Exception("Corner cannot be path")

        borders = [
            [cell for cell in self.row(0) if cell],
            [cell for cell in self.row(-1) if cell],
            [cell for cell in self.col(0) if cell],
            [cell for cell in self.col(-1) if cell],
        ]

        exits = [cell for border in borders for cell in border if cell]
        if len(exits) != 2:
            raise Exception("Expecting exactly 2 exits")


if __name__ == "__main__":
    assert sys.argv[1], 'Missing argument or not running through CLI'
    file = sys.argv[1]
    path = os.path.join(os.path.dirname(__file__), file)

    # generate your own maze img with: https://keesiemeijer.github.io/maze-generator/
    maze_path = i2m.get_maze_path(png=path)
    i2m.print_maze(matrix=maze_path)

    maze = Maze(matrix=maze_path)
    maze.check_borders_valid()
    print(maze.start_cell())
    print(maze.end_cell())
