import unittest

from errors import (
    MatrixSizeError,
    PathCornerError,
    PathExitAmountError,
    PathExitSpacingError,
)
from solve import Maze, Matrix, Validator, WindRose


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
        matrix2 = ((0, 0, 0), (1, 0, 0), (1, 0, 0), (0, 0, 0))
        maze1 = Maze(Matrix(matrix1))
        maze2 = Maze(Matrix(matrix2))
        self.assertRaises(PathExitSpacingError, Validator.exit_pos, *maze1.exit_nodes())
        self.assertRaises(PathExitSpacingError, Validator.exit_pos, *maze2.exit_nodes())

    def test_creep_finds_end_of_path_in_direction(self):
        matrix = (
            (0, 1, 0, 0, 0),
            (0, 1, 0, 1, 1),
            (0, 1, 1, 1, 0),
            (0, 0, 0, 0, 0),
        )
        maze = Maze(Matrix(matrix))
        n1_r, n1_c = maze.creep(0, 1, WindRose.S)
        n2_r, n2_c = maze.creep(n1_r, n1_c, WindRose.E)
        n3_r, n3_c = maze.creep(n2_r, n2_c, WindRose.N)
        n4_r, n4_c = maze.creep(n3_r, n3_c, WindRose.E)
        assert (n1_r, n1_c) == (2, 1)
        assert (n2_r, n2_c) == (2, 3)
        assert (n3_r, n3_c) == (1, 3)
        assert (n4_r, n4_c) == (1, 4)


if __name__ == "__main__":
    # overwrite constants to allow for more readable test matrices
    Maze.WALL = 0
    Maze.PATH = 1

    unittest.main()
