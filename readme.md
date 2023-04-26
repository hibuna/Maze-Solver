# Maze Solver

_Simple implementation of a maze solving algorithm._

---

## Example

![Solved maze (2000x2000)](https://i.imgur.com/A5jaQvQ.png)

---

## Usage

#### Step 1:
_Install [python](https://www.python.org/downloads/) v3.10 or higher._

#### Step 2:
_Download and unzip this repo and open the containing folder through a CLI:_

![cli](https://i.imgur.com/gXcm7b1.png)

#### Step 3:
_Create and activate a virtual environment to contain installed dependencies:_

`py -m venv venv && venv\Scripts\activate` (Windows)

#### Step 4:
_Download and install dependencies:_

`pip install -r requirements.txt`

#### Step 5 (Optional):
_Generate a maze with [this](https://keesiemeijer.github.io/maze-generator/#generate) tool and these settings:_

![generation settings](https://i.imgur.com/RmTazOq.png)


#### Step 6:
_Run the algorithm:_

`py solve.py "{path_to_generated_maze}"` max. 400x400\
`py solve.py "maze_small.png"` 400x400\
`py solve.py "maze_medium.png"` 1000x1000\
`py solve.py "maze_large.png"` 2000x2000
