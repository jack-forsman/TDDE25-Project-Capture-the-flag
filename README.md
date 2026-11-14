# Capture the Flag

Capture the Flag is a top-down tank game built with Python, Pygame, and
Pymunk. Players drive tanks around maze-like maps, collect the central flag,
and return it to their own base while trying to stop the opposing tanks with
projectiles.

The project supports both single-player mode, where the opposing tanks are
controlled by an AI, and local hot-seat multiplayer for two players sharing a
keyboard. It includes three selectable maps, physics-based movement and
collisions, destructible wooden obstacles, recoil when firing, respawn
protection, explosions, score tracking, sound effects, and background music.
A round is won by scoring three points.

## Controls

| Action | Player 1 | Player 2 |
| --- | --- | --- |
| Move forward/backward | `Up` / `Down` | `W` / `S` |
| Turn left/right | `Left` / `Right` | `A` / `D` |
| Fire | `Enter` | `Space` |

Use the menu to choose a game mode and map. Press `Escape` to exit.

## Getting started

Clone this repo and then remove the `.git` folder:
```
git clone https://gitlab.liu.se/tdde25/ctf
cd ctf
rm -rf .git
```
Then add your own git folder per the instructions on the TDDE25 git tutorial.


We also need to add the required libraries pymunk and pygame. We will do this using a [virtual environment](https://docs.python.org/3/tutorial/venv.html) in Python, which allows us to create an isolated environment for our project instead of installing the libraries system-wide.

To help with the process we created a script called `setup.sh` which you can source with:

```
source setup.sh
```

It activates a python environment and ensure you have the required libraries. You can then start the game with:

```
python3/python ctf.py
```

If you want to change the library version or use other python libraries, you should modify the `setup.sh` file so that your teachers can easilly check your code.

The environment will need to be activated in every new terminal that the project is run from. If using an IDE like VSCode it is recommended to [configure the interpreter](https://code.visualstudio.com/docs/python/environments#_select-and-activate-an-environment) for the project so that the environment is activated automatically.
