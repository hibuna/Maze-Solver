import unittest

from errors import MatrixSizeError, PathCornerError, PathExitError
from solve import Maze


class TestMaze(unittest.TestCase):
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
        self.assertRaises(MatrixSizeError, Maze.validate_matrix, matrix1)
        self.assertRaises(MatrixSizeError, Maze.validate_matrix, matrix2)

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
        self.assertRaises(PathCornerError, Maze.validate_matrix, matrix1)
        self.assertRaises(PathCornerError, Maze.validate_matrix, matrix2)

    def test_matrix_with_too_many_exits_raises_error(self):
        matrix = (
            (0, 1, 0),
            (1, 0, 0),
            (0, 1, 0),
        )
        self.assertRaises(PathExitError, Maze.validate_matrix, matrix)


if __name__ == '__main__':
    unittest.main()
