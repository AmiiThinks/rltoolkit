""" Gridworld GUI code
This file implements the GUI interface for a gridworld, using the simulation
object set up in the file guiwindow. The code is intended to be easily added to
or modified to customize for particular users or gridworld types.

The class GridworldView is the GUI view of the gridworld. This class can be
inherited and modified quite easily to display different aspects of a gridworld.
The following methods can be redefined to customize the interface:
   squareColor - chooses the color the square will be drawn with. Currently
     barriers are drawn as blue, and the value function is used for the others
   squareDrawColor - draws the color on the square
   squareDrawMore - a hook for you to draw your own stuff between the square
     coloring and the drawing of walls and arrows
   squareDrawWalls - draws the walls of the gridworld
   squareDrawArrows - draws arrows on the gridworld (currently using action values)
and for even more control, you can redefine:
   squareDrawContents
If you want to add your own controls for some events, you can redefine/modify:
   handleSquareClick - what to do if user clicks in a square

The class GridworldWindow is a specialized version of the SimulationWindow defined
in the file guiwindow. It adds menus and buttons specific to the gridworld
application. 
"""

from RLtoolkit.glue_guiwindow import *
from RLtoolkit.utilities import minmax, argmaxspecial
from .gwGlueAgent import *
from .gwGlueio import *

if sys.platform in ['mac', 'darwin']:
    walldiff = 3
else:
    walldiff = 3


class GridworldView(Gridworld, Gview):
    def __init__(self, parent, width=None, height=None,
                 startsquare=None, goalsquare=None, squaresize=60):
        Gridworld.__init__(self, width, height, startsquare, goalsquare)
        Gview.__init__(self, parent, windowTitle="Gridworld Window")
        if squaresize is None:
            squaresize = 60
        self.squaresize = squaresize
        self.minh = self.minv = 0
        self.update = True
        self.agentblock = None
        self.arrowdisplay = True
        self.colorsdisplay = True
        self.arrowcolor = gBlack
        self.maxarrowsize = 1
        self.wallpieces = []
        self.lastselectedx = None
        self.lastselectedy = None
        self.curevent = None
        self.contents = [[] for _ in range(self.numsquares)]
        gdSetViewportR(self,
                       0,
                       0,
                       self.width * self.squaresize,
                       self.height * self.squaresize)
        self.startandgoalfont = ("Helvetica", squaresize // 2, "bold")
        self.colors = [0 for _ in range(511)]
        for c in range(256):
            pos = 255 + c
            neg = 255 - c
            self.colors[pos] = gColorRGB255(self, 255 - c, 255, 255 - c)
            self.colors[neg] = gColorRGB255(self, 255, 255 - c, 255 - c)
        self.wallDisplay()

        self.agent = None
        self.task_agent_colors = False

    def gdClickEventHandler(self, dh, dv):  # GridworldView environment
        if self.dhdvInGridworldview(dh, dv):
            self.handleEventInEnvironment(dh, dv)

    def handleEventInEnvironment(self, dh, dv):
        square = self.squarefromdhdv(int(dh), int(dv))
        size = self.squaresize
        relativeh = dh - self.squaredh(square)
        relativev = dv - self.squaredv(square)
        scaledrelativeh = float(relativeh) / size
        scaledrelativev = float(relativev) / size
        centerselectedp = ((scaledrelativeh > .15) and
                           (scaledrelativeh < .85) and
                           (scaledrelativev > .15) and
                           (scaledrelativev < .85))
        if relativeh < 4:
            action = 2  # left
        elif relativev < 4:
            action = 0  # up
        elif relativeh > (size - 4):
            action = 3  # right
        elif relativev > (size - 4):
            action = 1  # down
        else:
            action = None

        if action is not None:
            self.toggleWall(square, action)
            self.squareDrawContents(self.agent, square)
        if centerselectedp:
            self.lastselectedx, self.lastselectedy = dh, dv
            if square == self.state:  # moving agent
                self.curevent = 'moveAgent'
            elif square == self.startsquare:  # moving start
                self.curevent = 'moveStart'
            elif square == self.goalsquare:  # moving goal
                self.curevent = 'moveGoal'
            else:
                self.handleSquareClick(self.agent, square)

    def handleSquareClick(self, agent, square):
        # toggle barrier status of square
        self.toggleBarrier(square)
        self.squareDrawContents(agent, square)

    def gdMouseUpEventHandler(self, dh, dv):  # finish event started
        dh, dv = int(dh), int(dv)
        if dh == self.lastselectedx and dv == self.lastselectedy:
            # do nothing; already handled
            pass
        elif self.curevent == 'moveAgent':
            square = self.squarefromdhdv(dh, dv)
            self.setState(square)
            self.agent.agent_start(self.state)
        elif self.curevent == 'moveStart':
            square = self.squarefromdhdv(dh, dv)
            self.resetStartSquare(self.agent, square)
        elif self.curevent == 'moveGoal':
            square = self.squarefromdhdv(dh, dv)
            self.resetGoalSquare(self.agent, square)
        self.lastselectedx = None
        self.lastselectedy = None
        self.curevent = None

    def gdMotionEventHandler(self, dx, dy):
        """Do the update at each motion event so that user can see the
        item being dragged"""
        dx, dy = int(dx), int(dy)
        if self.curevent == 'moveAgent':
            square = self.squarefromdhdv(dx, dy)
            self.setState(square)
        elif self.curevent == 'moveGoal':
            agent = self.agent
            square = self.squarefromdhdv(dx, dy)
            self.resetGoalSquare(agent, square)
        elif self.curevent == 'moveStart':
            agent = self.agent
            square = self.squarefromdhdv(dx, dy)
            self.resetStartSquare(agent, square)

    def squareDrawColor(self, agent, square):
        if self.contents[square] != [] and self.contents[square] is not None:
            gDelete(self, self.contents[square])
            self.contents[square] = []
        if self.barrierp[square]:
            color = gBlue
        else:
            color = self.squareColor(agent, square)
        self.contents[square].append(self.gFillSquare(square, color))

    def squareDrawMore(self, agent, square):
        pass

    def squareDrawStartGoal(self, agent, square):
        if square == self.startsquare:
            self.contents[square].append(self.drawLetterAtSquare(square, "S"))
        elif square == self.goalsquare:
            self.contents[square].append(self.drawLetterAtSquare(square, "G"))

    def squareDrawWalls(self, agent, square):
        for a in range(4):
            if self.wallp[square][a]:
                self.contents[square].append(self.drawWall(square, a))

    def squareDrawArrows(self, agent, square):
        avals = agent.actionvalues(square)
        for a in range(agent.numactions):
            value = avals[a]
            self.contents[square].append(self.drawSquareLine(square, a, value))
        bestaction, bestvalue = argmaxspecial(avals)
        if bestaction is not None:
            self.contents[square].append(
                self.drawSquareArrowhead(square, bestaction, bestvalue))

    def squareDrawContents(self, agent, square):
        # figure out better way to see what changes - dont redraw all
        if self.update:
            # if self.task_agent_colors:
            #     self.squareDrawColor(agent.task_agent, square)
            # else:
            self.squareDrawColor(agent, square)
            self.squareDrawMore(agent, square)
            self.squareDrawStartGoal(agent, square)
            if self.barrierp[square]:
                pass
            else:  # draw walls and arrows
                self.squareDrawWalls(agent, square)
                if not square == self.goalsquare and self.arrowdisplay:
                    self.squareDrawArrows(agent, square)

    def wallDisplay(self):
        """displays exterior walls"""
        maxx = self.squaresize * self.width
        maxy = self.squaresize * self.height
        gDelete(self, self.wallpieces)
        self.wallpieces = []
        for x in range(0, maxx, self.squaresize):
            self.wallpieces.append(gdDrawLine(self, x, 0, x, maxy, gGray))
        for y in range(0, maxy, self.squaresize):
            self.wallpieces.append(gdDrawLine(self, 0, y, maxx, y, gGray))

    def squareColor(self, agent, square):
        """square color is based on state value"""
        if not self.colorsdisplay:
            i = 255
        elif square == self.goalsquare:
            i = 510
        else:
            # value_range = np.max(agent.Q) - np.min(agent.Q)
            # if value_range:
            #     min_zero = agent.statevalue(square) - np.min(agent.Q)
            #     normalized_value = min_zero / max(value_range, 0.000001)
            #     min_neg_one = (normalized_value * 2) - 1
            # else:
            #     min_neg_one = 0

            # val = agent.statevalue(square)
            # if np.max(agent.Q) <= 0:
            #     if val == 0:
            #         val_adj = 0
            #     else:
            #         e_val = (val * 10 + 1) / (1 - (val * 10 + 1))
            #         if e_val < 0:
            #             val_adj = 0
            #         else:
            #             val_adj = np.log(e_val) / 7
            #     # print(val_adj)
            #
            #     val_adj = max(min(val_adj, 1), -1)
            # elif val <= 0:
            #     val_adj = -np.sqrt(2 * -val)
            # else:
            #     val_adj = np.sqrt(val / 5)
            #
            # # print(val, val_adj)
            # i = 255 + int(val_adj * 255)
            # # i = 255 + int(agent.statevalue(square) / 6 * 255)
            # i = max(0, i)

            val = agent.statevalue(square)
            # print(val)
            i = max(0, int(min(510, val * 255/5 + 255)))

        try:
            return self.colors[i]
        except IndexError:
            print(i, val)
            raise

    def drawWall(self, square, action):
        h = self.squaredh(square)
        v = self.squaredv(square)
        size = self.squaresize
        color = gBlue
        if action == 0:
            return gdDrawLineR(self, h + 1, v + 1, size - 2, 0, color)
        elif action == 1:
            return gdDrawLineR(self, h + 1, v + size - 1, size - 2, 0, color)
        elif action == 2:
            return gdDrawLineR(self, h + 1, v + 1, 0, size - 2, color)
        elif action == 3:
            return gdDrawLineR(self, h + size - 1, v + 1, 0, size - 2, color)

    def setState(self, newstate):
        self.state = newstate
        if self.update:
            if newstate is not None:
                self.flipStateDisplay(newstate)

    def flipStateDisplay(self, square):
        if self.agentblock is not None:
            gDelete(self, self.agentblock)
        if square == 'terminal':
            square = self.goalsquare
        self.agentblock = gdFillRectR(self,
                                      (self.squaresize // 4) + self.squaredh(
                                          square),
                                      (self.squaresize // 4) + self.squaredv(
                                          square),
                                      self.squaresize // 2,
                                      self.squaresize // 2, gOn)

    def gFillSquare(self, square, color):
        global walldiff
        return gdFillRectR(self, self.squaredh(square) + 1,
                           self.squaredv(square) + 1,
                           self.squaresize - walldiff,
                           self.squaresize - walldiff,
                           color)  # 3 instead of 2 for non mac

    def resetStartSquare(self, agent, newstartsquare):
        oldstart = self.startsquare
        self.startsquare = newstartsquare
        self.squareDrawContents(agent, oldstart)
        self.squareDrawContents(agent, newstartsquare)

    def resetGoalSquare(self, agent, newgoalsquare):
        oldgoal = self.goalsquare
        self.goalsquare = newgoalsquare
        self.squareDrawContents(agent, oldgoal)
        self.squareDrawContents(agent, newgoalsquare)

    def drawLetterAtSquare(self, square, letterstring):
        if square is not None:
            return gdDrawTextCentered(self, letterstring, self.startandgoalfont,
                                      (self.squaresize // 2) + self.squaredh(
                                          square),
                                      (self.squaresize // 2) + self.squaredv(
                                          square), gBlack)

    # ARROWS

    def drawSquareArrow(self, square, action):
        x = self.squaredh(square) + self.squaresize // 2
        y = self.squaredv(square) + self.squaresize // 2
        length = self.squaresize // 3
        if action == 0:
            return gdDrawArrow(self, x, y, x, y - length, self.arrowcolor)
        elif action == 1:
            return gdDrawArrow(self, x, y, x, y + length, self.arrowcolor)
        elif action == 2:
            return gdDrawArrow(self, x, y, x - length, y, self.arrowcolor)
        elif action == 3:
            return gdDrawArrow(self, x, y, x + length, y, self.arrowcolor)

    def setArrowDisplay(self, newdisplayp):
        self.arrowdisplay = newdisplayp
        self.whole_sim_display()

    def drawSquareLine(self, square, direction, length):
        halfsquaresize = self.squaresize // 2
        x = self.squaredh(square) + halfsquaresize
        y = self.squaredv(square) + halfsquaresize
        if length < 0:
            length = 0
        length = int(min(1., float(length) / self.maxarrowsize) *
                     halfsquaresize)
        if direction == 0:
            return gdDrawLine(self, x, y, x, y - length, self.arrowcolor)
        elif direction == 1:
            return gdDrawLine(self, x, y, x, y + length, self.arrowcolor)
        elif direction == 2:
            return gdDrawLine(self, x, y, x - length, y, self.arrowcolor)
        elif direction == 3:
            return gdDrawLine(self, x, y, x + length, y, self.arrowcolor)

    def drawSquareArrowhead(self, square, direction, length):
        halfsquaresize = self.squaresize // 2
        x = self.squaredh(square) + halfsquaresize
        y = self.squaredv(square) + halfsquaresize
        if length < 0:
            direction = (1 - direction) % 4  # opposite direction
        length = int(min(1.0, float(length) / self.maxarrowsize) *
                     halfsquaresize)
        if direction == 0:
            return gdDrawArrowhead(self, x, y, x, y - length, 0, 0.25,
                                   self.arrowcolor)
        elif direction == 1:
            return gdDrawArrowhead(self, x, y, x, y + length, 0, 0.25,
                                   self.arrowcolor)
        elif direction == 2:
            return gdDrawArrowhead(self, x, y, x - length, y, 0, 0.25,
                                   self.arrowcolor)
        elif direction == 3:
            return gdDrawArrowhead(self, x, y, x + length, y, 0, 0.25,
                                   self.arrowcolor)

    # Gridworld utilities
    def inverseaction(self, action):
        return (1 - action) % 4

    def squaredv(self, square):
        return self.minv + (self.squaresize * self.squarev(square))

    def squaredh(self, square):
        return self.minh + (self.squaresize * self.squareh(square))

    def dhdvInGridworldview(self, dh, dv):
        return ((dh >= self.minh) and (dv >= self.minv) and
               (dh <= (self.minh + (self.squaresize * self.width))) and
               (dv <= (self.minv + (self.squaresize * self.height))))

    def squarefromdhdv(self, dh, dv):
        return self.squarefromhv(
            max(0, min(self.width - 1, (dh - self.minh) // self.squaresize)),
            max(0, min(self.height - 1, (dv - self.minv) // self.squaresize)))


class GridworldWindow(SimulationWindow):
    def __init__(self, width=None, height=None, startsquare=None,
                 goalsquare=None,
                 squaresize=None, gridtype=GridworldView):
        wwidth = width * squaresize
        wheight = height * squaresize
        SimulationWindow.__init__(self, wwidth, wheight)
        self.gridview = gridtype(self, width, height, startsquare, goalsquare,
                                 squaresize)
        x1, y1, x2, y2 = gdGetViewport(self)  # get viewport info
        gdSetViewport(self, x1, y1, x2, y2 + 30)  # add enough for buttons
        gdAddButton(self, "DP Values", self.simAvi, 5, self.wheight - 30)
        gdAddButton(self, "Value It", self.simVI1, 100, self.wheight - 30)
        self.showpolicyarrows = gIntVar()
        self.showpolicyarrows.set(1)
        self.showvaluecolors = gIntVar()
        self.showvaluecolors.set(1)
        # self.showtaskagentcolors = gIntVar()
        # self.showtaskagentcolors.set(0)
        # self.task_agent_colors = False
        self.addGridworldMenu()
        self.addAgentMenu()
        self.addModelMenu()
        self.readtitle = "Choose Gridworld to Open"
        self.writetitle = "Save Current Gridworld As"
        self.initialdir = gwPath()

    def simAvi(self):
        if not isinstance(self.agent, DynaGridAgent):
            print("Cannot do DP on non model agent")
        else:
            avi(self.agent)
            self.whole_sim_display()

    def simVI1(self):
        if not isinstance(self.agent, DynaGridAgent):
            print("Cannot do Value Iteration on non model agent")
        else:
            vi1(self.agent)
            self.whole_sim_display()

    def update_sim_display(self):
        if self.agent is not None:
            # self.display(list(range(self.agent.numstates)))
            if self.num_ep_steps == 0:
                self.display(list(range(self.agent.numstates)))
            else:
                self.display(self.agent.changedstates)

    def display(self, displaystates):
        oldupdate = self.environment.update
        self.environment.update = True
        for sq in displaystates:
            self.environment.squareDrawContents(self.agent, sq)
        self.agent.changedstates = []
        # draw current agent location
        if self.environment.state is not None:
            self.environment.flipStateDisplay(self.environment.state)
        else:
            self.environment.flipStateDisplay(self.environment.startsquare)
        self.environment.update = oldupdate

    def whole_sim_display(self):
        self.environment.wallDisplay()
        agent = self.agent
        if agent is not None:
            self.display(list(range(agent.numstates)))

    # Opening and writing gridworld files

    def read_file(self, filename):
        if filename is not None and filename != '':
            lst = readGridworld(filename)
            gridworld = self.genGridworld(lst)
            set_window_title_from_namestring(gridworld, filename)

    def write_file(self, filename):
        olist = prepareWrite(self.gridview)
        writeGridworld(olist, filename)

    @staticmethod
    def genGridworld(alist, agentclass=DynaGridAgent):
        width, height, startsquare, goalsquare, barrierp, wallp = getgwinfo(
            alist)
        squaresize = alist.get('squaresize')
        gridworld = GridworldWindow(width, height, startsquare, goalsquare,
                                    squaresize)
        gview = gridworld.gridview

        if barrierp is not None:
            gview.barrierp = barrierp
        if wallp is not None:
            gview.wallp = wallp
        gview.updatedisplay = True

        gridworld.environment = gview
        gridworld.agent = agentclass(numstates=gview.numsquares,
                                     numactions=gview.numactions())
        gridworld.rl_init()
        gview.agent = gridworld.agent

        gridworld.whole_view()

    @staticmethod
    def makeNewSimulation(w=16, h=16, st=0, g=1, size=30,
                          agentclass=DynaGridAgent):
        s = GridworldWindow(width=w, height=h, startsquare=st, goalsquare=g,
                            squaresize=size)
        s.environment = s.gridview
        s.agent = agentclass(numstates=s.environment.numsquares,
                             numactions=s.environment.numactions())
        s.rl_init()
        s.gridview.agent = s.agent

        s.whole_view()

    # Agent stuff

    def changeagent(self, new_name):
        new_agent = changeAgentLearnMethod(self.environment, new_name)
        self.agent = new_agent
        self.agent.agent_init()
        self.rl_start()
        self.gridview.agent = self.agent
        self.whole_sim_display()

    def resetpar(self, name, value):
        eval('resetParameters(self.agent,' + name + '=' + str(value) + ')')

    def displayPars(self):
        displayParameters(self.agent)

    def initActionValues(self):
        saveQ(self.agent)
        for s in range(self.environment.numstates()):
            for a in range(self.environment.numactions()):
                self.agent.Q[s][a] = self.agent.initialvalue
        self.whole_sim_display()

    def revertValues(self):
        restoreQ(self.agent)
        self.whole_sim_display()

    def addAgentMenu(self):
        amenu = gAddMenu(self, "Agent",
                         [["New agent with One step Q learning",
                           lambda: self.changeagent("onestepq")],
                          ["New agent with Q(lambda)",
                           lambda: self.changeagent("qlambdareplace")],
                          ["New agent with Sarsa learning",
                           lambda: self.changeagent("sarsa")],
                          ["New agent with Sarsa(lambda)",
                           lambda: self.changeagent("sarsalambdatraces")],
                          ["New agent with One step dyna",
                           lambda: self.changeagent("onestepdyna")],
                          '---',
                          ["Init Values", self.initActionValues],
                          ["Revert Values", self.revertValues],
                          '---',
                          ["Display Agent Parameters",
                           lambda: self.displayPars()],
                          '---'])
        gAddMenu(amenu, "Change epsilon",
                 [["Set epsilon = 0.0", lambda: self.resetpar('epsilon', 0.0)],
                  ["Set epsilon = 0.01",
                   lambda: self.resetpar('epsilon', 0.01)],
                  ["Set epsilon = 0.05",
                   lambda: self.resetpar('epsilon', 0.05)],
                  ["Set epsilon = 0.1", lambda: self.resetpar('epsilon', 0.1)],
                  ["Set epsilon = 0.5", lambda: self.resetpar('epsilon', 0.5)],
                  ["Set epsilon = 1.0", lambda: self.resetpar('epsilon', 1.0)]])
        gAddMenu(amenu, "Change alpha",
                 [["Set alpha = 0.0", lambda: self.resetpar('alpha', 0.0)],
                  ["Set alpha = 0.1", lambda: self.resetpar('alpha', 0.1)],
                  ["Set alpha = 0.25", lambda: self.resetpar('alpha', 0.25)],
                  ["Set alpha = 0.5", lambda: self.resetpar('alpha', 0.5)],
                  ["Set alpha = 0.9", lambda: self.resetpar('alpha', 0.9)],
                  ["Set alpha = 1.0", lambda: self.resetpar('alpha', 1.0)]])
        gAddMenu(amenu, "Change gamma",
                 [["Set gamma = 0.0", lambda: self.resetpar('gamma', 0.0)],
                  ["Set gamma = 0.1", lambda: self.resetpar('gamma', 0.1)],
                  ["Set gamma = 0.5", lambda: self.resetpar('gamma', 0.5)],
                  ["Set gamma = 0.9", lambda: self.resetpar('gamma', 0.9)],
                  ["Set gamma = 1.0", lambda: self.resetpar('gamma', 1.0)]])
        gAddMenu(amenu, "Change lambda",
                 [["Set lambda = 0.0",
                   lambda: self.resetpar('agentlambda', 0.0)],
                  ["Set lambda = 0.5",
                   lambda: self.resetpar('agentlambda', 0.5)],
                  ["Set lambda = 0.8",
                   lambda: self.resetpar('agentlambda', 0.8)],
                  ["Set lambda = 1.0",
                   lambda: self.resetpar('agentlambda', 1.0)]])
        gAddMenu(amenu, "Change exploration bonus",
                 [["Set expl bonus = 0.0",
                   lambda: self.resetpar('explorationbonus', 0.0)],
                  ["Set expl bonus = 0.0001",
                   lambda: self.resetpar('explorationbonus', 0.0001)],
                  ["Set expl bonus = 0.001",
                   lambda: self.resetpar('explorationbonus', 0.001)],
                  ["Set expl bonus = 0.01",
                   lambda: self.resetpar('explorationbonus', 0.01)]])
        gAddMenu(amenu, "Change initial value",
                 [["Set initial value = -0.1",
                   lambda: self.resetpar('initialvalue', -0.1)],
                  ["Set initial value = 0.0",
                   lambda: self.resetpar('initialvalue', 0.0)],
                  ["Set initial value = 0.01",
                   lambda: self.resetpar('initialvalue', 0.01)],
                  ["Set initial value = 0.1",
                   lambda: self.resetpar('initialvalue', 0.1)],
                  ["Set initial value = 0.5",
                   lambda: self.resetpar('initialvalue', 0.5)],
                  ["Set initial value = 1.0",
                   lambda: self.resetpar('initialvalue', 1.0)]])

    def toggleShowArrows(self):
        self.gridview.arrowdisplay = not self.gridview.arrowdisplay
        self.whole_sim_display()

    def toggleShowColors(self):
        self.gridview.colorsdisplay = not self.gridview.colorsdisplay
        self.whole_sim_display()

    # def toggleTaskAgentColors(self):
    #     self.task_agent_colors = not self.task_agent_colors
    #     self.whole_sim_display()

    # model stuff

    def correctModel(self):
        setupAccurateModel(self)
        avi(self.agent)
        self.whole_sim_display()

    def emptyModel(self):
        setupNullModel(self)
        avi(self.agent)
        self.whole_sim_display()

    def setModelNoObstacles(self):
        setupEmptyGridModel(self)
        avi(self.agent)
        self.whole_sim_display()

    def setModelStay(self):
        setupStayModel(self.agent)
        avi(self.agent)
        self.whole_sim_display()

    def revealGoal(self):
        revealGoalLocation(self)
        self.whole_sim_display()

    def revertModel(self):
        restoreModel(self.agent)
        self.whole_sim_display()

    def addGridworldMenu(self):
        m = gAddMenu(self, "Gridworld",
                     [
                         ['button', "Show Policy Arrows", self.showpolicyarrows,
                          1, 0,
                          lambda: self.toggleShowArrows()],
                         ['button', "Show Value Colors", self.showvaluecolors,
                          1, 0,
                          lambda: self.toggleShowColors()],
                         # ['button', "Show Task Agent Colors",
                         #  self.showtaskagentcolors,
                         #  1, 0,
                         #  lambda: self.toggleTaskAgentColors()],
                         "---",
                         ["6 x 8 gridworld",
                          lambda: self.read_file(gwFilename('gw8x6'))],
                         ["16 x 10 gridworld",
                          lambda: self.read_file(gwFilename('gw16x10'))],
                         ["16 x 10 cleared gridworld",
                          lambda: self.read_file(gwFilename('gw16x10cleared'))],
                         ["16 x 16 cleared gridworld",
                          lambda: self.read_file(gwFilename('gw16x16'))],
                         '---'])
        gAddMenu(m, "New Gridworld",
                 [["4x1", lambda: GridworldWindow.makeNewSimulation(4, 1, 0, 3, 80)],
                  ["2x2", lambda: GridworldWindow.makeNewSimulation(2, 2, 0, 3, 160)],
                  ["8x1", lambda: GridworldWindow.makeNewSimulation(8, 1, 0, 3, 80)],
                  ["4x4", lambda: GridworldWindow.makeNewSimulation(4, 4, 0, 15, 80)],
                  ["8x6", lambda: GridworldWindow.makeNewSimulation(8, 6, 0, 47, 70)],
                  ["6x8", lambda: GridworldWindow.makeNewSimulation(6, 8, 0, 47, 70)],
                  ["8x8", lambda: GridworldWindow.makeNewSimulation(8, 8, 0, 47, 70)],
                  ["10x10", lambda: GridworldWindow.makeNewSimulation(10, 10, 0, 99, 60)],
                  ["10x16", lambda: GridworldWindow.makeNewSimulation(10, 16, 0, 159, 40)],
                  ["16x10", lambda: GridworldWindow.makeNewSimulation(16, 10, 0, 159, 60)],
                  ["16x16", lambda: GridworldWindow.makeNewSimulation(16, 16, 0, 255, 40)],
                  ["20x20", lambda: GridworldWindow.makeNewSimulation(20, 20, 0, 399, 30)],
                  ["40x40",
                   lambda: GridworldWindow.makeNewSimulation(40, 40, 0, 1599,
                                                             20)]])

    def addModelMenu(self):
        gAddMenu(self, "Model",
                 [["DP Values", self.simAvi],
                  ["Value Iteration", self.simVI1],
                  '---',
                  ["Correct Model", lambda: self.correctModel()],
                  ["Empty Model", lambda: self.emptyModel()],
                  ["No Obstacles Model", lambda: self.setModelNoObstacles()],
                  ["Stay Model", lambda: self.setModelStay()],
                  ["Reveal Goal", lambda: self.revealGoal()],
                  '---',
                  ["Revert Model", lambda: self.revertModel()]])


###

def makeGridworldSimulation(w=16, h=16, st=0, g=1, size=30,
                            gridworldclass=GridworldWindow,
                            agentclass=DynaGridAgent):
    s = gridworldclass(width=w, height=h, startsquare=st, goalsquare=g,
                       squaresize=size)
    s.environment = s.gridview
    s.agent = agentclass(numstates=s.environment.numsquares,
                         numactions=s.environment.numactions())
    s.rl_init()

    return s

