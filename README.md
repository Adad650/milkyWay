# Echo Maze

Echo Maze is a 2-dimensional maze escape game where you pilot a defective robot who was built without a camera but has an extra speaker and uses echolocation to map out its surroundings.

## Play Online

You can play the game directly in your browser by opening `index.html` or by running the Flask server.

## Local Development

### Web Version (Recommended)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Flask server:
   ```bash
   python app.py
   ```

3. Open your browser and go to:
   ```
   http://localhost:5000
   ```

### Original Pygame Version

1. Install Pygame:
   ```bash
   python3 -m pip install PyGame
   ```

2. Run the game:
   ```bash
   python main.py
   ```

## Game Controls
- **WASD** - Move the robot
- **Click** - Emit an echo pulse to reveal walls
- **Find the green exit** to advance to the next level

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

## Future improvements/upgrades:
- A story that goes with the game
- Enemies
- A png image for the player
