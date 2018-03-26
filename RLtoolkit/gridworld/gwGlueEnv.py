""" This is gridworld code for use standalone, with or without display onto 
an arbitrary gview, or in conjunction with the standard RL interface.  

The walls are stateaction pairs which leave you in the same square rather
than taking you to your neighboring square.  If there were no walls,
wraparound would occur at the gridworld edges# we start with walls all
around the edges.

The barriers (squares you can't pass into) are overlaid on top of this.

The goal square is a terminal state.
Reward is +1 for reaching the goal, 0 else.
"""


class Gridworld:
    def __init__(self, width=8, height=6, startsquare=0, goalsquare=1):
        if width is None:
            width = 8
        if height is None:
            height = 6
        if startsquare is None:
            startsquare = 0
        if goalsquare is None:
            goalsquare = 1
        self.width = width
        self.height = height
        self.numsquares = self.width * self.height
        self.startsquare = startsquare
        self.goalsquare = goalsquare
        self.state = None
        self.barrierp = None
        self.wallp = None

    def env_init(self):
        self.state = None
        self.barrierp = [False for _ in range(self.numsquares)]
        self.wallp = [[False for _ in range(4)] for _ in range(self.numsquares)]
        for v in range(self.height):  # setup walls at gridworld borders
            self.toggleWall(self.squarefromhv(0, v), 2)
            self.toggleWall(self.squarefromhv(self.width - 1, v), 3)
        for h in range(self.width):
            self.toggleWall(self.squarefromhv(h, 0), 0)
            self.toggleWall(self.squarefromhv(h, self.height - 1), 1)

    def env_start(self):
        self.state = self.startsquare
        return self.startsquare

    def env_step(self, action):
        self.state = self.gridworldnextstate(self.state, action)
        if self.state == 'terminal':
            reward = 1
        else:
            reward = 0
        return reward, self.state, self.state == 'terminal'

    def numactions(self):
        return 4

    def numstates(self):
        return self.numsquares

    def toggleWall(self, square, action):
        self.wallp[square][action] = not self.wallp[square][action]

    def toggleBarrier(self, square):
        self.barrierp[square] = not self.barrierp[square]

    def squareh(self, square):
        return square % self.width

    def squarev(self, square):
        return int(square / self.width)

    def squarefromhv(self, h, v):
        s = v * self.width + h
        return s

    def neighboringSquares(self, square):
        sqs = []
        for action in range(4):
            sqs.append(self.neighboringSquare(square, action))
        return sqs

    def neighboringSquare(self, square, action):
        h = self.squareh(square)  # horizontal
        v = self.squarev(square)  # vertical
        if action == 0:
            return self.squarefromhv(h, (v - 1) % self.height)  # up
        elif action == 1:
            return self.squarefromhv(h, (v + 1) % self.height)  # down
        elif action == 2:
            return self.squarefromhv((h - 1) % self.width, v)  # left
        else:
            return self.squarefromhv((h + 1) % self.width, v)  # right

    def gridworldnextstate(self, s, a):
        if self.wallp[s][a]:
            return s
        else:
            proposednextstate = self.neighboringSquare(s, a)
            if self.barrierp[proposednextstate]:
                return s
            elif proposednextstate == self.goalsquare:
                return 'terminal'
            else:
                return proposednextstate


class ObjectGridworld(Gridworld):
    def __init__(self, width=8, height=6, startsquare=0, goalsquare=1):
        Gridworld.__init__(self, width, height, startsquare, goalsquare)
        self.objects = None

    def env_init(self):
        Gridworld.env_init(self)
        self.objects = [None for _ in range(self.numsquares)]

    def env_start(self):
        self.state = self.startsquare
        return self.startsquare

    def env_step(self, action):
        self.state = self.gridworldnextstate(self.state, action)
        if self.state == 'terminal':
            reward = 1
        else:
            reward = 0
            extra = self.objects[self.state]
            if extra is not None:
                if isinstance(extra, (list, tuple)):
                    reward += extra[1]
                    if extra[0] == 'consumable':  # remove object - used up
                        self.objects[self.state] = None
                else:  # number reward, treat as permanent
                    reward += extra
        return reward, self.state, self.state == 'terminal'

    def addObject(self, square, value, otype='permanent'):
        self.objects[square] = [otype, value]

    def removeObject(self, square):
        self.objects[square] = None
