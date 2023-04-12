import os
import sys

import image2matrix as i2m



if __name__=="__main__":
    assert sys.argv[1], 'Missing argument or not running through CLI'
    file = sys.argv[1]
    path = os.path.join(os.path.dirname(__file__), file)

    # generate your own maze img with: https://keesiemeijer.github.io/maze-generator/
    maze_walls = i2m.get_maze_path(png=path, inverted=True)
    i2m.print_maze(matrix=maze_walls)
