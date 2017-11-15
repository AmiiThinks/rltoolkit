"""
This is gridworld code with a graphical display and user interface.
For non graphical gridworld, use gwDemoN.py

There are three main objects:
   Gridworld          Just the environment with no graphics stuff
   Gridworldview      A gridworld with view (graphics related stuff)
   GridworldWindow    A simulation window to hold the gridworldview with buttons for simulation

The walls are stateaction pairs which leave you in the same square rather
than taking you to your neighboring square.  If there were no walls, wraparound
would occur at the gridworld edges.
We start with walls all around the edges.

The barriers (squares you can't pass into) are overlaid on top of this.

The goal square is a terminal state.  Reward is +1 for reaching the goal, 0 else.
"""

###

from .gwobject import *


def runDemo():
    makeGridworldSimulation(16, 16, 87, 15, 30)
    gMainloop()


def runObjDemo():
    makeObjectGridworldSimulation(25, 25, 87, 15, 24)

    gMainloop()


def makeObjectGridworldSimulation(w=16, h=16, st=0, g=1, size=30,
                                  agentclass=DynaGridAgent):
    s = ObjectGridworldWindow(width=w, height=h, startsquare=st, goalsquare=g,
                              squaresize=size)
    env = s.gridview
    agent = agentclass(numstates=env.numsquares, numactions=env.numactions())
    simInit(s, agent, env, False)
    return s

if __name__ == '__main__':
    runObjDemo()
