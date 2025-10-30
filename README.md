# Echo Maze



Echo Maze is a 2-dimensional maze escape game built in Python with Pygame. You pilot a defective robot who was built without a camera but has an extra speaker and uses echolocation to map out its surroundings.

## Requirements
- Python 3.10 or newer
- `pygame`


Install the dependency:
Install the dependency:

```bash
python3 -m pip install PyGame
```

## Clone repo in a folder

```bash
git clone https://github.com/Adad650/milkyWay
```

## Runing the game

```bash
python3 main.py
```

## Controls
- `W`, `A`, `S`, `D`: Moving through maze
- `Shift`: Move faster while held
- Left click for "echo"
- `Esc` or `cmd + Q` or `alt + F4`

## Gameplay overview
- The maze is randomly generated each run, so the layout will always be different.
- Left click sends out an expanding pulse that temporarily reveals nearby passages and walls.
- Pulses have a short cooldown; plan your movement so you are not caught in darkness.
- Reach the green tile in the bottom-right corner to escape the maze.
## Gameplay overview
- The maze is randomly generated each run, so the layout is different each time.
- Left click send out a short pulse displaying the maze allowing you to navigate.
- Pulses have a cooldown so use them smartly.
- Reach the green tile in the botton right to escape the maze. 

Feel free to tweak the constants in `main.py` (Cooldown for echo, color, etc.)to play around.
