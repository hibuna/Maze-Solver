import unittest

from errors import MatrixSizeError, PathCornerError, PathExitError
from solve import Maze, Matrix, Validator


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
        self.assertRaises(PathExitError, Validator.exit_cell_amt, matrix)

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
            (0, 0, 0)
        )
        maze1 = Maze(Matrix(matrix1))
        maze2 = Maze(Matrix(matrix2))
        self.assertRaises(
            PathExitError, Validator.exit_cell_pos, *maze1.exit_cells()
        )
        self.assertRaises(
            PathExitError, Validator.exit_cell_pos, *maze2.exit_cells()
        )


if __name__ == '__main__':
    unittest.main()
