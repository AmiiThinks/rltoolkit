from gridworld.gwGlueAgent import QlambdaGridAgent
from rl_glue import RLGlue


# Random walk example using RL Glue

class Environment:
    "Random walk environment"

    def __init__(self, numstates, numactions=2):
        self.numactions = numactions
        self.numstates = numstates
        self.curstate = None

    def env_init(self):
        self.curstate = None

    def env_start(self):
        """Returns the initial state"""
        self.curstate = self.numstates // 2  # start in the middle
        # print "Environment initializing state to", self.curstate
        return self.curstate

    def env_step(self, a):
        """Does the action and returns reward, next state, and terminal"""
        terminal = False
        if a == 0:
            self.curstate -= 1  # First action, go left
        elif a == self.numactions - 1:
            self.curstate += 1  # Last action, go right

        if self.curstate == 0:  # reached left end
            terminal = True
            r = -1
        elif self.curstate == self.numstates - 1:  # reached right end
            terminal = True
            r = 1
        else:
            r = 0
        return r, self.curstate, terminal


if __name__ == '__main__':
    env = Environment(10)
    agent = QlambdaGridAgent(numstates=env.numstates,
                             numactions=env.numactions,
                             epsilon=0.1, alpha=0.1, gamma=0.9)

    glue = RLGlue(env, agent)

    glue.rl_init()

    for i in range(30):
        reward = glue.total_reward
        eps = glue.rl_episode(0)
        print(f"Episode took {glue.num_ep_steps} steps, received " +
              f'{glue.total_reward - reward} reward')
