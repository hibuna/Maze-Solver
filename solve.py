import enum
import os
import sys
from typing import Optional, Iterable
from dataclasses import dataclass

import image2matrix as i2m
import matrix2image as m2i
from errors import (
    MatrixSizeError,
    PathCornerError,
    PathExitAmountError,
    PathExitSpacingError,
)


class Type:
    Cell = tuple[int, int]
    Row = tuple[bool, ...]
    Col = tuple[bool, ...]
    Matrix = tuple[Row, ...]


@dataclass
class Node:
    cell: Type.Cell
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
    def __init__(self, matrix: Type.Matrix):
        self.matrix = matrix
        self.width = len(matrix[0])
        self.height = len(matrix)

    def row(self, index: int) -> Type.Row:
        i = index if index >= 0 else (index * -1) - 1  # equalize negative index
        if i >= self.height:
            raise IndexError(f"Index out of bounds: {index}")
        return self.matrix[index]

    def col(self, index: int) -> Type.Col:
        i = index if index >= 0 else (index * -1) - 1  # equalize negative index
        if i >= self.width:
            raise IndexError(f"Index out of bounds: {index}")
        return tuple([row[index] for row in self.matrix])

    def cell(self, cell: Type.Cell):
        row, col = cell
        return self.matrix[row][col]

    def cells(self) -> list[Type.Cell]:
        cells = []
        for row in range(self.height):
            for col in range(self.width):
                if self.matrix[row][col]:
                    cells.append((row, col))
        return cells


class Maze:
    def __init__(self, matrix: Matrix):
        self.mx = matrix
        self.bst_root: BST = None
        self.solution: list = []
        self.node_start: Node = None
        self.node_end: Node = None

    WALL = False
    PATH = True

    def solve(self):
        self.find_exit_cells()
        self.create_nodes()
        self.find_solution()

    def find_solution(self) -> list[Type.Cell]:
        solution = [self.node_end.cell]
        cell = self.node_end.cell
        direction = self.node_end.origin
        while True:
            node = self.creep(cell, direction, traceback=True, save_path_to=solution)
            if node is self.node_start:
                break
            cell = node.cell
            direction = node.origin

        self.solution = solution
        return solution

    def creep(
        self,
        cell: Type.Cell,
        direction: WindRose,
        save_path_to: list = None,
        traceback: bool = False,
    ) -> Node:
        """Creep down a path and around corners to find the next junction or dead end."""
        while True:
            cell = self.walk(cell, direction, save_path_to=save_path_to)
            if self.is_node(cell):  # TODO: optimize by pruning dead ends?
                if traceback:
                    return self.bst_root.find(cell)
                return self.create_node(cell, origin=WindRose.opposite(direction))
            direction = self.find_adjacent(cell, except_=WindRose.opposite(direction))[0]

    def walk(
        self,
        cell: Type.Cell,
        direction: WindRose,
        save_path_to: list = None,
    ) -> Type.Cell:
        """Walk from a point until you find a node, hit a wall or move outside the matrix.
        Return row, col of the cell before either happens."""
        cell_next = self.take_step(cell, direction, save_path_to=save_path_to)
        while self.take_step(cell_next, direction):
            if self.is_node(cell_next):
                break
            cell_next = self.take_step(cell_next, direction, save_path_to=save_path_to)
        return cell_next

    def take_step(
        self,
        cell: Type.Cell,
        direction: WindRose,
        save_path_to: list = None,
    ) -> Type.Cell:
        row, col = cell
        d_row, d_col = direction.value
        cell_next = (row + d_row, col + d_col)
        if self.is_traversable(cell_next):
            if save_path_to is not None:
                save_path_to.append(cell_next)
            return cell_next

    def find_adjacent(
        self, cell: Type.Cell, except_: Optional[WindRose] = None
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
        cell_start, cell_end = self.find_exit_cells()
        self.node_start = self.create_node(cell_start, origin=None)

        self.bst_root = BST(self.node_start)

        # While checking a node, append all existing neighbour Nodes to the stack.
        # After having checked all directions, remove the node from the stack and
        # repeat the proces with the first encountered neighbour node
        recursion_stack = [self.node_start]
        while True:
            node = recursion_stack[0]
            for direction in WindRose:
                if direction in node.checked:
                    continue
                if not self.take_step(node.cell, direction):
                    node.checked.append(direction)
                    continue

                next_node = self.creep(node.cell, direction)
                recursion_stack.append(next_node)
                node.checked.append(direction)

            self.bst_root.add(node)

            if len(node.checked) == 4:
                recursion_stack.remove(node)

            if not recursion_stack:
                break

        # Set origin of ending Node to set up traceback
        self.node_end = self.bst_root.find(cell_end)
        self.node_end.origin = self.find_adjacent(cell_end)[0]  # only possible neighbour

        return self.bst_root

    def find_exit_cells(self) -> tuple[Type.Cell, Type.Cell]:
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

        return cells

    @staticmethod
    def create_node(
            cell: Type.Cell,
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

    def is_traversable(self, cell: Type.Cell):
        row, col = cell
        crossed_borders = (
            row < 0,
            row >= self.mx.height,
            col < 0,
            col >= self.mx.width,
        )
        return not any(crossed_borders) and self.mx.cell(cell) is Maze.PATH

    def is_node(self, cell: Type.Cell):
        return len(self.find_adjacent(cell)) != 2

    def is_junction(self, cell: Type.Cell):
        return len(self.find_adjacent(cell)) in (3, 4)


class BST:
    """Binary Search Tree"""
    def __init__(self, maze_node: Node) -> None:
        self.key = sum(maze_node.cell)
        self.maze_nodes = [maze_node]
        self.left = None
        self.right = None

    def _search(self, key) -> tuple["BST", bool]:
        bst = self
        while True:
            if key < bst.key:
                if not bst.left:
                    return bst, False
                elif bst.left.key == key:
                    return bst.left, True
                else:
                    bst = bst.left
            elif key > bst.key:
                if not bst.right:
                    return bst, False
                elif bst.right.key == key:
                    return bst.right, True
                else:
                    bst = bst.right
            else:
                return bst, True

    def add(self, maze_node: Node) -> None:
        key = sum(maze_node.cell)
        bst, found = self._search(key)
        if found and maze_node not in bst.maze_nodes:
            bst.maze_nodes.append(maze_node)
            return
        if not found and key < bst.key:
            bst.left = BST(maze_node)
        if not found and key > bst.key:
            bst.right = BST(maze_node)

    def find(self, cell: Type.Cell):
        bst_node, found = self._search(sum(cell))
        if not found:
            return
        for node in bst_node.maze_nodes:
            if node.cell == cell:
                return node


class Validator:
    @staticmethod
    def validate(matrix: Type.Matrix):
        Validator.size(matrix)
        Validator.corners(matrix)
        Validator.exit_amt(matrix)

        maze = Maze(Matrix(matrix))
        Validator.exit_pos(maze)

    @staticmethod
    def size(matrix: Type.Matrix) -> None:
        if len(matrix) < 3 or any(len(row) < 3 for row in matrix):
            raise MatrixSizeError("Matrix must be at least 3x3")

    @staticmethod
    def corners(matrix: Type.Matrix) -> None:
        corners = [
            matrix[0][0],
            matrix[0][-1],
            matrix[-1][0],
            matrix[-1][-1],
        ]
        if any(corners):
            raise PathCornerError("Corner cannot be path")

    @staticmethod
    def exit_amt(matrix: Type.Matrix) -> None:
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
        node_start, node_end = maze.find_exit_cells()
        row_start, col_start = node_start
        row_end, col_end = node_end
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

    Validator.validate(matrix=maze_path)
    maze = Maze(Matrix(maze_path))
    maze.solve()

    target_file = f"{file.split('.')[0]} - solved.png"
    target = os.path.join(os.path.dirname(__file__), target_file)
    m2i.create_png(target, (maze.mx.width, maze.mx.height), maze.mx.cells(), maze.solution)
