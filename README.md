# RLtoolkit
Version 2.0 b0 August 17, 2018


## To use:
1. Recommended: `python3 -m pip install git+https://github.com/AmiiThinks/rltoolkit.git`
   
   Alternate:
   Move the RLtoolkit folder to your site-packages folder for Python
                               OR
   `export PYTHONPATH=$PYTHONPATH:/path/to/rltoolkit`

2. You can then import as you would any other package

    In Python:
    ```pythonstub
    from RLtoolkit import tiles3.tiles as tiles
    from RLtoolkit.rl_glue import RLGlue
    etc.
    ```
    From the command line:
    ```pythonstub
    python -m RLtoolkit.examples.mountain_car_gui.py
    ```
        

## Contents:

- **examples** - a folder of demos to run, using the toolkit
  - mountain car (GUI)
  - random walk (text-based)
  - gridworld (GUI)
  - gridworld (text-based)
- **gridworld** - gridworld code, including a demo
- **G** - a general low level graphics drawing package
- **Quickgraph** - a simple graphing package (uses g) for 2 and 3d graphs

- **rl_glue** - main interface for connecting agents and environments
- **utilities** - some general utilities
- **glue_guiwindow** - a generic simulation window with buttons and menus
   (not yet documented for users, uses RL-Glue)
- **tiles3** - the tile coding package from http://www.incompleteideas.net/tiles/tiles3.html

