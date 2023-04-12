import numpy as np

from PIL import Image


def get_maze_path(png: str, inverted: bool = False):
    img = Image.open(png).convert("RGB")
    array = np.array(img).tolist()

    wall = [255, 255, 255]

    maze_wall_matrix = []
    for row in array:
        maze_wall_matrix.append((cell == wall for cell in row))

    maze_wall_matrix = tuple((tuple(row) for row in maze_wall_matrix))

    return maze_wall_matrix


def print_maze(matrix, ch='H', sep=' '):
    for row in matrix:
        for px in row:
            s = ch + sep if px else ' ' + sep
            print(s, end='')
        print()
