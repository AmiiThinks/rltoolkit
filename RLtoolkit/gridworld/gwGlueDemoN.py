""" This is gridworld code with no graphical interfaced
For a graphical interface, use gwgui.py

The walls are stateaction pairs which leave you in the same square rather than taking you
to your neighboring square.  If there were no walls, wraparound would occur at the gridworld edges
We start with walls all around the edges.

The barriers (squares you can't pass into) are overlaid on top of this.

The goal square is a terminal state.  Reward is +1 for reaching the goal, 0 else.
"""
import os.path

from RLtoolkit.rl_glue import RLGlue
from .gwAgent import *
from .gwGlueio import *


class GWDemoN(RLGlue):
    def __init__(self,
                 height=6,
                 width=8,
                 start=0,
                 goal=47,
                 alpha=0.5,
                 gamma=0.9,
                 epsilon=0.05,
                 agentlambda=0.8,
                 initialvalue=.1,
                 verbose=False):
        self.verboseV = verbose
        env = Gridworld(width, height, start, goal)
        agent = DynaGridAgent(4, self.environment.numstates(), epsilon, alpha, gamma,
                              initialvalue,
                              agentlambda)
        RLGlue.__init__(env, agent)
        self.rl_init()

    def episode(self, max_steps):
        self.rl_episode(max_steps)

    def wall(self, square, action):
        if action in range(4):
            if (int(square) == square and 0 <= square < 
                    self.environment.numsquares):
                self.environment.toggleWall(square, action)
            else:
                print("Square '{}' is not a legal square".format(square))
        else:
            print("Action '{}' is not a legal action".format(action))

    def barrier(self, square):
        if int(square) == square and 0 <= square < self.environment.numsquares:
            self.environment.toggleBarrier(square)
        else:
            print("Square '{}' is not a legal square".format(square))

    def new_agent(self, newlearn='onestepdyna'):
        """Legal values for newlearn are 'onestepdyna', 'qlambdareplace',
                                         'onestepq' and 'sarsalambdatraces' """
        if newlearn == 'qlambdareplace':  # Q(lambda), replace traces
            newagent = QlambdaGridAgent(self.environment.numactions(),
                                        self.environment.numstates())
        elif newlearn == 'onestepq':  # one step Q learner
            newagent = QonestepGridAgent(self.environment.numactions(),
                                         self.environment.numstates())
        elif newlearn == 'onestepdyna':  # one step dyna
            newagent = DynaGridAgent(self.environment.numactions(),
                                     self.environment.numstates())
        elif newlearn == 'sarsalambdatraces':  # Sarsa(lambda), replace traces
            newagent = SarsaLambdaGridAgent(self.environment.numactions(),
                                            self.environment.numstates())
        elif newlearn == 'sarsa':  # Sarsa(lambda), replace traces
            newagent = SarsaGridAgent(self.environment.numactions(),
                                      self.environment.numstates())
        else:
            newagent = None

        if newagent is not None:
            self.agent = newagent
            self.rl_init()

    def read(self, file, alpha=0.5, gamma=0.9, epsilon=0.05, agentlambda=0.8, \
               explorationbonus=0, initialvalue=.1, verbose=False):
        if not os.path.isabs(file):
            file = gwFilename(file)
        lst = readGridworld(file)
        self.gen_gridworld_n(lst, alpha, gamma, epsilon, agentlambda,
                             explorationbonus, initialvalue, verbose)

    def gen_gridworld_n(self, alist, alpha=0.5, gamma=0.9, epsilon=0.05,
                        agentlambda=0.8, explorationbonus=0, initialvalue=.1,
                        verbose=False, agentclass=DynaGridAgent):
        self.verboseV = verbose
        (width, height, startsquare, goalsquare,
         barrierp, wallp) = getgwinfo(alist)
        env = Gridworld(width, height, startsquare, goalsquare)
        if barrierp is not None:
            env.barrierp = barrierp
        if wallp is not None:
            env.wallp = wallp
        self.agent = agentclass(4, self.environment.numstates(), epsilon,
                                alpha, gamma, initialvalue, agentlambda)
        self.environment = env
        self.agent = agent
        self.rl_init()

    def obj_read(self, file, alpha=0.5, gamma=0.9, epsilon=0.05,
                 agentlambda=0.8, explorationbonus=0, initialvalue=.1,
                 verbose=False):
        if not os.path.isabs(file):
            file = gwFilename(file)
        lst = readGridworld(file)
        self.gen_obj_gridworld_n(lst, alpha, gamma, epsilon, agentlambda,
                                 explorationbonus, initialvalue, verbose)

    def gen_obj_gridworld_n(self, alist, alpha=0.5, gamma=0.9, epsilon=0.05,
                            agentlambda=0.8, explorationbonus=0,
                            initialvalue=.1, verbose=False):
        self.verboseV = verbose
        (width, height, startsquare, goalsquare,
         barrierp, wallp) = getgwinfo(alist)
        objects = alist.get('objects')
        self.environment = ObjectGridworld(width, height, startsquare,
                                           goalsquare)
        if barrierp is not None:
            self.environment.barrierp = barrierp
        if wallp is not None:
            self.environment.wallp = wallp
        if objects is not None:
            self.environment.objects = objects

        self.agent = DynaGridAgent(4, self.environment.numstates(), epsilon,
                                   alpha, gamma, initialvalue, agentlambda)
        self.rl_init()

    def display_par(self, agent=None):
        if agent is None:
            agent = self.agent
        displayParameters(agent)

    def set_par(self, agent=None, alpha=None, gamma=None, epsilon=None,
                agentlambda=None, explorationbonus=None, initialvalue=None):
        if agent is None:
            agent = self.agent
        resetParameters(agent, alpha, gamma, epsilon, agentlambda,
                        explorationbonus, initialvalue)


def gwHelp():
    print("""Gridworld demo:
   To set up your gridworld, use
      gwInit(height, width, start, goal, alpha, gamma, epsilon,
             agentlambda, explorationbonus, initialvalue, verbose)
         numepisodes is the number of episodes to run (default is 1)
         height is the number of squares high the gridworld is (default is 6)
         width is the number of squares wide the gridworld is (default is 8)
           squares are numbered from 0 to height x width - 1
         start is the square the agent starts from (default 0)
         goal is the goal square (default 47)
         alpha is the learning rate (default 0.5)
         gamma is the discount rate (default 0.9)
         epsilon is the exploration rate (default 0.05)
         agentlambda is lambda (default 0.8)
         explorationbonus is the exploration bonus (default 0)
         initial value is the value to start the Q values at (default is 0.1)
         verbose is whether or not to print each action and state (default False)
    Note: squares are numbered from 0 to height x width - 1

   Optionally add walls and barriers to your gridworld:
      The walls are stateaction pairs which leave you in the same square rather
      than taking you to your neighboring square.  If there were no walls,
      wraparound would occur at the gridworld edges. We start with walls all around
      the edges. The barriers (squares you can't pass into) are overlaid on top of this.

      gwWall(square, action)
         adds a wall in the square specified by square for the action specified
         by action (0-left, 1-up, 2-right, 3-down)
         If there is already a wall there, this removes it.
      gwBarrier(square)
         makes square a barrier square (filled in). If the square was already a barrier,
         this makes it a normal square (non barrier)

   Albernatively, read in a gridworld using:
      gwRead("filename", alpha, gamma, epsilon, agentlambda, explorationbonus, 
              initialvalue, verbose)
         where filename specifies one of the files in the Gridworlds folder
           (e.g. "gw16x10") or the entire pathname of a file anywhere else
         the other parameters are as for gwInit, above

   The default agent uses one step dyna as its learning method. To change the agent:
      gwNewAgent(newlearn)
         where newlearn is one of
            'onestepq' - one step Q learning
            'qlambdareplace' - q lambda replacing traces
            'onestepdyna' - one step dyna
            'sarsalambdatraces' - sarsa lambda with traces
      gwSetPar(agent, alpha, gamma, epsilon, agentlambdam explorationbonus, initialvalue)
         changes specified parameters. The agent defaults to the current agent.
      gwDisplayPar(agent)
         displays the type and parameters for the agent specified
           (defaults to the current agent)

   To run simulations on the gridworld (after gwInit or gwRead has been run), use:
      gwEpisode()      runs one episode
      gwEpisodes(num)  runs num episodes
   both return the number of steps required to reach the goal for each episode
   """)


if __name__ == '__main__':
    gwHelp()
