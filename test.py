import unittest
from unittest.mock import patch

from errors import (
    MatrixSizeError,
    PathCornerError,
    PathExitAmountError,
    PathExitSpacingError,
)
from solve import Maze, Matrix, Validator, WindRose, BST


class BSTMock:
    def __init__(self, *args, **kwargs):
        self.nodes = []

    def add(self, node: dict):
        self.nodes.append(node)


class TestMatrix(unittest.TestCase):
    def test_matrix_too_small_raises_error(self):
        matrix1 = (
            (0, 1, 0),
            (0, 0),
            (0, 1, 0),
        )
        matrix2 = (
            (0, 1, 0),
            (0, 0, 1),
        )
        self.assertRaises(MatrixSizeError, Validator.size, matrix1)
        self.assertRaises(MatrixSizeError, Validator.size, matrix2)

    def test_matrix_with_corner_path_raises_error(self):
        matrix1 = (
            (1, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        )
        matrix2 = (
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 1),
        )
        self.assertRaises(PathCornerError, Validator.corners, matrix1)
        self.assertRaises(PathCornerError, Validator.corners, matrix2)

    def test_matrix_with_too_many_exits_raises_error(self):
        matrix = (
            (0, 1, 0),
            (1, 0, 0),
            (0, 1, 0),
        )
        self.assertRaises(PathExitAmountError, Validator.exit_amt, matrix)

    def test_row_out_of_bounds(self):
        matrix = (
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        )
        matrix = Matrix(matrix)
        self.assertRaises(IndexError, matrix.row, 3)
        self.assertRaises(IndexError, matrix.row, -4)

    def test_row_returns_expected(self):
        matrix = (
            (1, 0, 0),
            (0, 0, 1),
            (0, 1, 0),
        )
        matrix = Matrix(matrix)
        assert matrix.row(1) == (0, 0, 1)
        assert matrix.row(-1) == (0, 1, 0)

    def test_col_out_of_bounds(self):
        matrix = (
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        )
        matrix = Matrix(matrix)
        self.assertRaises(IndexError, matrix.row, 3)
        self.assertRaises(IndexError, matrix.row, -4)

    def test_col_returns_expected(self):
        matrix = (
            (1, 0, 0),
            (0, 0, 1),
            (0, 1, 0),
        )
        matrix = Matrix(matrix)
        assert matrix.col(1) == (0, 0, 1)
        assert matrix.col(-1) == (0, 1, 0)


class MazeTest(unittest.TestCase):
    def test_maze_exits_neighbouring_raises_error(self):
        matrix1 = (
            (0, 1, 1, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        )
        matrix2 = (
            (0, 0, 0),
            (1, 0, 0),
            (1, 0, 0),
            (0, 0, 0),
        )
        maze1 = Maze(Matrix(matrix1))
        maze2 = Maze(Matrix(matrix2))
        self.assertRaises(PathExitSpacingError, Validator.exit_pos, maze1)
        self.assertRaises(PathExitSpacingError, Validator.exit_pos, maze2)

    def test_walk_finds_end_of_path_in_direction(self):
        matrix = (
            (0, 1, 0, 0, 0),
            (0, 1, 0, 1, 1),
            (0, 1, 1, 1, 0),
            (0, 0, 0, 0, 0),
        )
        maze = Maze(Matrix(matrix))
        node1 = maze.walk((0, 1), WindRose.S)
        node2 = maze.walk(node1, direction=WindRose.E)
        node3 = maze.walk(node2, direction=WindRose.N)
        node4 = maze.walk(node3, direction=WindRose.E)
        assert node1 == (2, 1)
        assert node2 == (2, 3)
        assert node3 == (1, 3)
        assert node4 == (1, 4)

    def test_walk_finds_end_or_node_in_direction(self):
        matrix = (
            (0, 1, 0, 0, 0),
            (0, 1, 0, 0, 0),
            (0, 1, 1, 1, 0),
            (0, 0, 1, 0, 0),
        )
        maze = Maze(Matrix(matrix))
        cell1 = maze.walk((0, 1), WindRose.S)
        cell2 = maze.walk(cell1, WindRose.E)
        cell3 = maze.walk(cell2, WindRose.S)
        assert cell1 == (2, 1)
        assert cell2 == (2, 2)
        assert cell3 == (3, 2)

    def test_creep_walks_around_corners(self):
        matrix1 = (
            (0, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 0, 1, 0),
            (0, 0, 1, 0),
        )
        matrix2 = (
            (0, 1, 0, 0),
            (0, 1, 1, 1),
            (0, 0, 1, 0),
            (0, 0, 0, 0),
        )
        maze1 = Maze(Matrix(matrix1))
        maze2 = Maze(Matrix(matrix2))
        node1 = maze1.creep((0, 1), WindRose.S)
        node2 = maze2.creep((0, 1), WindRose.S)
        assert node1["cell"] == (3, 2)
        assert node2["cell"] == (1, 2)

    def test_create_nodes_creates_all_nodes(self):
        matrix1 = (
            (0, 1, 0, 0, 0),
            (0, 1, 1, 1, 0),
            (0, 0, 1, 0, 0),
            (0, 1, 1, 1, 1),
            (0, 0, 0, 0, 0),
        )
        matrix2 = (
            (0, 0, 1, 0, 0),
            (0, 1, 1, 1, 0),
            (0, 0, 1, 0, 0),
            (1, 1, 1, 1, 0),
            (0, 0, 0, 0, 0),
        )
        maze1 = Maze(Matrix(matrix1))
        maze2 = Maze(Matrix(matrix2))

        # mock BST to just return a list of created nodes
        with patch("solve.BST", BSTMock):
            nodes1 = maze1.create_nodes().nodes
            nodes2 = maze2.create_nodes().nodes

        cells1 = [node["cell"] for node in nodes1]
        cells2 = [node["cell"] for node in nodes2]

        assert len(cells1) == 6
        assert len(cells2) == 7
        assert (0, 1) in cells1
        assert (1, 2) in cells1
        assert (1, 3) in cells1
        assert (3, 2) in cells1
        assert (3, 1) in cells1
        assert (3, 4) in cells1
        assert (0, 2) in cells2
        assert (1, 2) in cells2
        assert (1, 1) in cells2
        assert (1, 3) in cells2
        assert (3, 2) in cells2
        assert (3, 3) in cells2
        assert (3, 0) in cells2

    def test_create_nodes_sets_attrs_correctly(self):
        matrix = (
            (0, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 1, 0, 0),
        )
        maze = Maze(Matrix(matrix))

        # mock BST to just return a list of created nodes
        with patch("solve.BST", BSTMock):
            nodes = maze.create_nodes().nodes

        for node in nodes:
            assert len(node["checked"]) == 4
            for direction in WindRose:
                assert direction in node["checked"]

            if node["cell"] == (0, 1):
                assert node["origin"] is None
            elif node["cell"] == (1, 1):
                assert node["origin"] is WindRose.N
            elif node["cell"] == (1, 2):
                assert node["origin"] is WindRose.W
            elif node["cell"] == (2, 1):
                assert node["origin"] is WindRose.N
            else:
                assert 0


class BinarySearchTreeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Expected BST structure
        # ---------------------
        #    100
        # 50 / \ 150
        #          \ 200 x2
        #        175 / \ 225 x2
        # ---------------------
        cls.root_cell = {"cell": (0, 100)}
        cls.root_l_cell = {"cell": (0, 50)}
        cls.root_r_cell = {"cell": (0, 150)}
        cls.root_rr_cell1 = {"cell": (0, 200)}
        cls.root_rr_cell2 = {"cell": (100, 100)}
        cls.root_rrl_cell = {"cell": (175, 0)}
        cls.root_rrr_cell1 = {"cell": (0, 225)}
        cls.root_rrr_cell2 = {"cell": (225, 0)}

        bst_root = BST(cls.root_cell)
        bst_root.add(cls.root_l_cell)
        bst_root.add(cls.root_r_cell)
        bst_root.add(cls.root_rr_cell1)
        bst_root.add(cls.root_rr_cell2)
        bst_root.add(cls.root_rrl_cell)
        bst_root.add(cls.root_rrr_cell1)
        bst_root.add(cls.root_rrr_cell2)

        cls.root = bst_root
        cls.root_l = bst_root.left
        cls.root_r = bst_root.right
        cls.root_rr = bst_root.right.right
        cls.root_rrl = bst_root.right.right.left
        cls.root_rrr = bst_root.right.right.right

    def test_tree_has_expected_structure(self):
        assert self.root.left is self.root_l
        assert self.root_l.left is None
        assert self.root_l.right is None
        assert self.root_r.left is None
        assert self.root_r.right is self.root_rr
        assert self.root_rr.right is self.root_rrr
        assert self.root_rr.left is self.root_rrl
        assert self.root_rrl.left is None
        assert self.root_rrl.right is None
        assert self.root_rrr.left is None
        assert self.root_rrr.right is None

    def test_tree_has_expected_keys(self):
        assert self.root.key == 100
        assert self.root_l.key == 50
        assert self.root_r.key == 150
        assert self.root_rr.key == 200
        assert self.root_rrl.key == 175
        assert self.root_rrr.key == 225

    def test_tree_has_correct_nodes(self):
        assert len(self.root.maze_nodes) == 1
        assert len(self.root_l.maze_nodes) == 1
        assert len(self.root_r.maze_nodes) == 1
        assert len(self.root_rr.maze_nodes) == 2
        assert len(self.root_rrl.maze_nodes) == 1
        assert len(self.root_rrr.maze_nodes) == 2
        assert self.root_cell in self.root.maze_nodes
        assert self.root_l_cell in self.root_l.maze_nodes
        assert self.root_r_cell in self.root_r.maze_nodes
        assert self.root_rr_cell1 in self.root_rr.maze_nodes
        assert self.root_rr_cell2 in self.root_rr.maze_nodes
        assert self.root_rrl_cell in self.root_rrl.maze_nodes
        assert self.root_rrr_cell1 in self.root_rrr.maze_nodes
        assert self.root_rrr_cell2 in self.root_rrr.maze_nodes

    def test_search_returns_correct_node(self):
        assert self.root._search(100)[0].maze_nodes[0] is self.root_cell
        assert self.root._search(50)[0].maze_nodes[0] is self.root_l_cell
        assert self.root._search(150)[0].maze_nodes[0] is self.root_r_cell
        assert self.root_rr_cell1 in self.root._search(200)[0].maze_nodes
        assert self.root_rr_cell2 in self.root._search(200)[0].maze_nodes
        assert self.root._search(175)[0].maze_nodes[0] is self.root_rrl_cell
        assert self.root_rrr_cell1 in self.root._search(225)[0].maze_nodes
        assert self.root_rrr_cell2 in self.root._search(225)[0].maze_nodes

    def test_find_finds_node(self):
        node = self.root.find((0, 225))
        assert node is self.root_rrr_cell1

    def test_find_does_not_find_non_existent_node(self):
        node = self.root.find((1, 1))
        assert node is None


if __name__ == "__main__":
    # overwrite constants to allow for more readable test matrices
    Maze.WALL = 0
    Maze.PATH = 1

    unittest.main()
