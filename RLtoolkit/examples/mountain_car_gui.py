# This is an example program for reinforcement learning with linear function
# approximation. The learning algorithm used is sarsa(lambda) with traces.

# This is the GUI version of mountain car. Simply import/load it and it will
# display a graphical interface to the mountain car simulation. You can run
# episodes from there.

# Written by Rich Sutton 12/17/00
# Converted to Python in April, 2004
# Modified to use the RL interface in April 2004
# Modified to use the RL-Glue interface by Niko Yasui August 2018

import numpy as np

from RLtoolkit.Quickgraph.graph3d import *
from RLtoolkit.glue_guiwindow import SimulationWindow
from RLtoolkit.gridworld.gwGlueAgent import QlambdaGridAgent
from RLtoolkit.tiles3 import IHT, tiles


class MCWindow(SimulationWindow):
    def __init__(self, update, wwidth=340, wheight=660, **kwargs):
        del kwargs
        gheight = GDEVICE.wheight
        if wheight >= gheight:
            wwidth = int((gheight - 100) / float(wheight) * wwidth)
            wheight = gheight - 100
        super().__init__(wwidth, wheight)

        gSetTitle(self, "Mountain Car")
        gSetCS(self, 0, 20, 340, 680, 'lowerLeft')

        self.mcarTopView = Gview(self)
        gSetViewport(self.mcarTopView, 20, 360, 320, 660)
        gSetCS(self.mcarTopView, -1.2, -0.07, 0.6, 0.07)

        self.mcarSideView = Gview(self)
        gSetViewport(self.mcarSideView, 20, 100, 320, 345)
        gSetCS(self.mcarSideView, -1.2, -1.1, 0.6, 1.1)
        gClear(self, 'blue')

        self.displays = self.displayt = self.oldtop = self.oldside = []

        self.update = update

    def whole_sim_display(self):
        self.draw_view()
        self.update()
        gMakeVisible(self)

    def update_sim_display(self):
        self.draw_view()
        gMakeVisible(self)

    @staticmethod
    def car_height(position):
        return np.sin(3 * position)

    @staticmethod
    def car_slope(position):
        return np.cos(3 * position)

    def draw_view(self):
        gDelete(self.mcarSideView, self.displays)
        gDelete(self.mcarTopView, self.displayt)
        self.displays = self.displayt = []

        self.displays.append(gClear(self.mcarSideView, 'blue'))
        self.displayt.append(gClear(self.mcarTopView, 'purple'))
        self.displayt.append(gFillRect(self.mcarTopView, 0.5,
                                       -0.07, 0.6,
                                       0.07, 'green'))
        self.displayt.append(gDrawLine(self.mcarTopView, -1.2, 0,
                                       0.6, 0, 'light gray'))

        # draw mountain
        lasty = lastx = None
        radius, delta = 0.09, 0.01
        pos = -1.2
        for i in range(int((0.6 - -1.2) / delta)):
            slope = self.car_slope(pos)
            angle = atan(slope)
            x = pos + (radius * sin(angle))
            y = self.car_height(pos) - (radius * cos(angle))
            if lastx is not None:
                self.displays.append(gDrawLine(self.mcarSideView, lastx, lasty,
                                               x, y, 'white'))
            lastx = x
            lasty = y
            pos += delta
        self.displays.append(gDrawLineR(self.mcarSideView, 0.5,
                                        self.car_height(0.5) - 0.09,
                                        0, -.1, 'white'))
        self.draw_state()

    def draw_state(self):
        vel, pos = self.environment.vel, self.environment.pos
        gDelete(self.mcarTopView, self.oldtop)
        self.oldtop = list()
        self.oldtop.append(gDrawDisk(self.mcarTopView, pos, vel, .033, 'white'))
        self.displayt.append(gDrawPoint(self.mcarTopView, pos, vel, 'white'))
        self.draw_side()

    def draw_side(self):
        pos = self.environment.pos
        h = self.car_height(pos)

        # erase previous disk and arrow
        gDelete(self.mcarSideView, self.oldside)
        self.oldside = list()
        self.oldside.append(gDrawDisk(self.mcarSideView, pos, h, 0.065,
                                      'white'))
        d = .1
        if self.last_action == 2:
            self.oldside.append(gDrawArrow(self.mcarSideView, pos + d,
                                           h, pos + d + d, h, 'white'))
        elif self.last_action == 0:
            self.oldside.append(gDrawArrow(self.mcarSideView, pos - d,
                                           h, pos - d - d, h, 'white'))


class G3DGraph(Gwindow):
    def __init__(self, res, update, **kwargs):
        Gwindow.__init__(self, **kwargs)
        self.res = res
        self.data = [[0 for _ in range(self.res)] for _ in range(self.res)]
        gdAddButton(self, "update", update, 5, 5, 'dark blue')
        self.grbits = []

    def gDrawView(self):
        gDelete(self, self.grbits)
        self.grbits = graphSurface(self, self.data)
        gMakeVisible(self)

    def gDestroy(self, event):  # quit if this is last window 
        Gwindow.gDestroy(self, event)
        if not GDEVICE.childwindows:
            gQuit()


class Visualizer:
    def __init__(self, res):
        self.mc_window = MCWindow(self.g3d_update,
                                  windowTitle="State-value Function")
        self.g3d_graph = G3DGraph(res, self.g3d_update)
        self.g3d_graph.gDrawView()
        gdSetViewportR(self.g3d_graph, 350, 20, 400, 400)

        self.mc_rl_start = self.mc_window.rl_start
        self.mc_window.rl_start = self.rl_start

    def rl_start(self):
        """Rewrite the rl_start function to call the graph update before
        each episode."""
        self.g3d_update()
        self.mc_rl_start()

    def g3d_update(self):
        for i in range(self.g3d_graph.res):
            pos = -1.2 + ((0.6 - -1.2) * (float(i) / (self.g3d_graph.res - 1)))
            for j in range(self.g3d_graph.res):
                vel = (2 * 0.07 * (j / (self.g3d_graph.res - 1))) - 0.07
                if pos >= 0.5:
                    d = 0.0
                else:
                    try:
                        phi = self.mc_window.environment.get_phi((vel, pos))
                    except AttributeError:
                        phi = self.mc_window.agent.get_phi(np.array([vel, pos]))
                    d = self.mc_window.agent.statevalue(phi)
                self.g3d_graph.data[i][j] = d
        self.g3d_graph.gDrawView()


class MCEnvironment:
    def __init__(self, num_tiles=np.array([2, 2]), num_tilings=32):
        self.vel = None
        self.pos = None
        self.actions = [-1, 0, 1]

        self.num_tilings = num_tilings
        self.size = (num_tiles + 1).prod() * self.num_tilings
        self.scale = num_tiles / np.array([0.14, 1.7])
        self.iht = None

    def env_init(self):
        self.iht = IHT(self.size)

    def get_phi(self, state):
        floats = ((np.asarray(state) + [0.07, 1.2]) * self.scale).tolist()
        return tiles(self.iht, self.num_tilings, floats)

    def env_start(self):
        self.vel = 0
        self.pos = np.random.uniform(-0.6, -0.4)
        state = self.vel, self.pos

        return self.get_phi(state)

    def env_step(self, action):
        self.vel += 0.001 * self.actions[action] - 0.0025 * np.cos(3 * self.pos)
        self.vel = min(max(-0.07, self.vel), 0.07)
        self.pos += self.vel
        self.pos = min(max(-1.2, self.pos), 0.5)

        if self.pos == -1.2:
            self.vel = 0

        state = self.vel, self.pos

        terminal = self.pos == 0.5
        reward = -1

        return reward, self.get_phi(state), terminal

    def numactions(self):
        return len(self.actions)

    def numstates(self):
        # number of cells
        return self.size


def rundemo():
    s = Visualizer(30)
    env = MCEnvironment()
    s.mc_window.environment = env
    s.mc_window.agent = QlambdaGridAgent(numactions=env.numactions(),
                                         numstates=env.numstates(),
                                         epsilon=0.01,
                                         alpha=0.5 / env.num_tilings,
                                         agentlambda=0.9,
                                         gamma=1)
    s.mc_window.rl_init()
    s.mc_window.environment.vel = 0
    s.mc_window.environment.pos = -0.5
    s.mc_window.whole_view()
    gMainLoop()


if __name__ == '__main__':
    rundemo()
