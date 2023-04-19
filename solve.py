import enum
import os
import sys
from typing import Optional, Iterable
from dataclasses import dataclass

import image2matrix as i2m
from errors import (
    MatrixSizeError,
    PathCornerError,
    PathExitAmountError,
    PathExitSpacingError,
)

CellType = tuple[int, int]
RowType = ColType = tuple[bool, ...]
MatrixType = tuple[RowType, ...]


@dataclass
class Node:
    cell: CellType
    origin: Optional["WindRose"]
    checked: list["WindRose"]


class WindRose(enum.Enum):
    N = -1, 0
    E = 0, 1
    S = 1, 0
    W = 0, -1

    @staticmethod
    def opposite(direction: "WindRose") -> "WindRose":
        match direction:
            case(WindRose.N):
                return WindRose.S
            case(WindRose.E):
                return WindRose.W
            case(WindRose.S):
                return WindRose.N
            case(WindRose.W):
                return WindRose.E

    @staticmethod
    def all():
        return [direction for direction in WindRose]


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

    def cell(self, cell: CellType):
        row, col = cell
        return self.matrix[row][col]


class Maze:
    def __init__(self, matrix: Matrix):
        self.mx = matrix
        self.bst_root: BST = None
        self.solution: list = []
        self.node_start: Node = None
        self.node_end: Node = None

    WALL = False
    PATH = True

    def creep(
        self,
        cell: CellType,
        direction: WindRose,
        traceback: bool = False
    ) -> Node:
        """Creep down a path and around corners to find the next junction or dead end."""
        while True:
            cell = self.walk(cell, direction)
            if self.is_node(cell):  # TODO: optimize by pruning dead ends?
                if traceback:
                    return self.bst_root.find(cell)
                return self.create_node(cell, origin=WindRose.opposite(direction))
            direction = self.find_adjacent(cell, except_=WindRose.opposite(direction))[0]

    def walk(
        self,
        cell: CellType,
        direction: WindRose,
    ) -> CellType:
        """Walk from a point until you find a node, hit a wall or move outside the matrix.
        Return row, col of the cell before either happens."""
        cell_next = self.take_step(cell, direction)
        while self.take_step(cell_next, direction):
            if self.is_node(cell_next):
                break
            cell_next = self.take_step(cell_next, direction)
        return cell_next

    def take_step(
        self,
        cell: CellType,
        direction: WindRose,
    ) -> CellType:
        row, col = cell
        d_row, d_col = direction.value
        cell_next = (row + d_row, col + d_col)
        if self.is_traversable(cell_next):
            return cell_next

    def find_adjacent(
        self, cell: CellType, except_: Optional[WindRose] = None
    ) -> list[WindRose]:
        directions = []
        for direction in WindRose:
            cell_adj = self.take_step(cell, direction)
            if cell_adj is None:
                continue
            if self.mx.cell(cell_adj) is Maze.PATH:
                directions.append(direction)
        if except_ and except_ in directions:
            directions.remove(except_)
        return directions

    def create_nodes(self) -> "BST":

        def recursive_creep(node: Node):
            for direction in WindRose:
                if direction in node.checked:
                    continue
                if not self.take_step(node.cell, direction):
                    node.checked.append(direction)
                    continue
                node_tmp = self.creep(node.cell, direction)
                recursive_creep(node_tmp)
                node.checked.append(direction)
            self.bst_root.add(node)

        node_start, _ = self.exit_nodes()
        self.bst_root = BST(node_start)
        recursive_creep(node_start)
        return self.bst_root

    def exit_nodes(self) -> tuple[Node, Node]:
        cells = []
        north_border = self.mx.row(0)
        east_border = self.mx.col(-1)
        south_border = self.mx.row(-1)
        west_border = self.mx.col(0)

        for i in range(self.mx.width):
            if north_border[i] is Maze.PATH:
                cells.append((0, i))
            if south_border[i] is Maze.PATH:
                cells.append((self.mx.height - 1, i))

        for i in range(self.mx.height):
            if east_border[i] is Maze.PATH:
                cells.append((i, self.mx.width - 1))
            if west_border[i] is Maze.PATH:
                cells.append((i, 0))

        start_cell, end_cell = cells
        start_node = self.create_node(start_cell, origin=None)
        end_node = self.create_node(end_cell, origin=None)
        return start_node, end_node

    @staticmethod
    def create_node(
            cell: CellType,
            origin: Optional[WindRose],
            checked: Iterable[WindRose] = None,
    ) -> Node:
        if checked is None:
            checked = []
        if origin not in checked and origin is not None:
            checked.append(origin)

        return Node(
            cell=cell,
            origin=origin,
            checked=list(checked),
        )

    def is_traversable(self, cell: CellType):
        row, col = cell
        crossed_borders = (
            row < 0,
            row >= self.mx.height,
            col < 0,
            col >= self.mx.width,
        )
        return not any(crossed_borders) and self.mx.cell(cell) is Maze.PATH

    def is_node(self, cell: CellType):
        return len(self.find_adjacent(cell)) != 2

    def is_junction(self, cell: CellType):
        return len(self.find_adjacent(cell)) in (3, 4)


class BST:
    """Binary Search Tree"""
    def __init__(self, maze_node: Node) -> None:
        self.key = sum(maze_node.cell)
        self.maze_nodes = [maze_node]
        self.left = None
        self.right = None

    def _search(self, key) -> tuple["BST", bool]:
        if key < self.key:
            if self.left:
                return self.left._search(key)
            return self, False
        elif key > self.key:
            if self.right:
                return self.right._search(key)
            return self, False
        return self, True

    def add(self, maze_node: Node) -> None:
        key = sum(maze_node.cell)
        leaf, found = self._search(key)
        if found and maze_node not in leaf.maze_nodes:
            leaf.maze_nodes.append(maze_node)
            return
        if not found and key < leaf.key:
            leaf.left = BST(maze_node)
        if not found and key > leaf.key:
            leaf.right = BST(maze_node)

    def find(self, cell: CellType):
        bst_node, found = self._search(sum(cell))
        if not found:
            return
        for node in bst_node.maze_nodes:
            if node.cell == cell:
                return node


class Validator:
    @staticmethod
    def validate(matrix: MatrixType):
        Validator.size(matrix)
        Validator.corners(matrix)
        Validator.exit_amt(matrix)

        maze = Maze(Matrix(matrix))
        Validator.exit_pos(maze)

    @staticmethod
    def size(matrix: MatrixType) -> None:
        if len(matrix) < 3 or any(len(row) < 3 for row in matrix):
            raise MatrixSizeError("Matrix must be at least 3x3")

    @staticmethod
    def corners(matrix: MatrixType) -> None:
        corners = [
            matrix[0][0],
            matrix[0][-1],
            matrix[-1][0],
            matrix[-1][-1],
        ]
        if any(corners):
            raise PathCornerError("Corner cannot be path")

    @staticmethod
    def exit_amt(matrix: MatrixType) -> None:
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
    def exit_pos(maze: Maze) -> None:
        node_start, node_end = maze.exit_nodes()
        row_start, col_start = node_start.cell
        row_end, col_end = node_end.cell
        d_y = abs(row_start - row_end)
        d_x = abs(col_start - col_end)
        if d_x == 0 and d_y == 1 or d_y == 0 and d_x == 1:
            raise PathExitSpacingError("Exits must be at least 1 cell apart")


if __name__ == "__main__":
    assert sys.argv[1], "Missing argument or not running through CLI"
    file = sys.argv[1]
    path = os.path.join(os.path.dirname(__file__), file)

    # generate your own maze img with: https://keesiemeijer.github.io/maze-generator/
    maze_path = i2m.get_maze_path(png=path)
    i2m.print_maze(matrix=maze_path)

    Validator.validate(matrix=maze_path)
    maze = Maze(Matrix(maze_path))
