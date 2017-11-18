"""Gui code for gridworld with objects/rewards
This code is based on the general gridworld GUI code in gwguimain. It specializes
both the gridworld gui object and the simulation object.
Note: negative consumable rewards may not disappear when they are consumed until
the square is redrawn for some other reason.
"""

from RLtoolkit.utilities  import strlist
from .gwGlueguimain import *


class ObjectGridworldView(ObjectGridworld, GridworldView):
    def __init__(self, parent, width=None, height=None,
                 startsquare=None, goalsquare=None, squaresize=60):
        GridworldView.__init__(self, parent, width, height,
                               startsquare, goalsquare, squaresize)
        ObjectGridworld.__init__(self, width, height, startsquare, goalsquare)
        self.clickBarrier = True
        self.curvalue = 1.0
        self.curtype = 'permanent'
        self.lowObjValue = -1.0
        self.highObjValue = 1.0
        self.objIncr = 0.1

    def handleSquareClick(self, agent, square):
        """click can add barrier or object, not just barrier
        """
        if not self.clickBarrier:  # add or remove object
            if self.objects[square] is not None:
                self.removeObject(square)
            else:
                self.addObject(square, self.curvalue, self.curtype)
            self.squareDrawContents(agent, square)
        else:  # toggle barrier status of square
            self.toggleBarrier(square)
            self.squareDrawContents(agent, square)

    def squareDrawMore(self, agent, square):
        """draw objects"""
        if self.objects[square] is not None:
            self.contents[square].append(self.drawObject(agent,
                                                         square,
                                                         self.objects[square]))

    def drawObject(self, agent, square, objectrep):
        if isinstance(objectrep, (tuple, list)):
            return self.gFillObject(square, objectrep[1], objectrep[0])
        else:
            return self.gFillObject(square, objectrep)

    def objectColor(self, value):
        """want value between 0 and 511 (0 to 254 negative, 255 0, 256 to 511
        # positive)"""
        value = value / self.highObjValue
        i = 255 + int(minmax(value, -1, 1) * 255)
        return self.colors[i]

    def gFillObject(self, square, value, otype='permanent'):
        mid = int(self.squaresize / 2)
        dx = self.squaredh(square)
        dy = self.squaredv(square)
        color = self.objectColor(value)
        radius = int(self.squaresize / 3)
        if otype == 'permanent':
            return (gdDrawDisk(self, dx + mid + 1, dy + mid + 1, radius, color),
                    gdDrawCircle(self, dx + mid + 1, dy + mid + 1, radius,
                                 'black'))
        else:  # consumable
            return (gdDrawWedge(self, dx + mid + 1, dy + mid + radius,
                                2 * radius, 50, 80, color),
                    gdDrawArc(self, dx + mid + 1, dy + mid + radius, 2 * radius,
                              50, 80, 'black'))


class ObjectGridworldWindow(GridworldWindow):
    def __init__(self, width=None, height=None, startsquare=None,
                 goalsquare=None, squaresize=None):
        GridworldWindow.__init__(self, width, height, startsquare, goalsquare,
                                 squaresize, ObjectGridworldView)
        x1, y1, x2, y2 = gdGetViewport(self)
        gdSetViewport(self, x1, y1, x2, y2 + 30)  # add enough for buttons
        buttony = self.wheight - 30
        self.addbutton = gdAddButton(self, "Click means barrier",
                                     self.setObject, 5, buttony)
        gSetTitle(self, "Object Gridworld Simulation")
        gdAddButton(self, "-", self.decrObjValue, 170, buttony)
        self.valbutton = gdAddButton(self, "1.0", None, 210, buttony)
        gdAddButton(self, "+", self.incrObjValue, 270, buttony)
        self.typebutton = gdAddButton(self, 'permanent', self.changeType, 320,
                                      buttony)
        self.addObjectMenu()

    @staticmethod
    def makeNewSimulation(w=16, h=16, st=0, g=1, size=30,
                          agentclass=DynaGridAgent):
        s = ObjectGridworldWindow(width=w, height=h, startsquare=st,
                                  goalsquare=g, squaresize=size)
        s.environment = s.gridview
        s.agent = agentclass(numstates=s.environment.numsquares,
                             numactions=s.environment.numactions())
        s.gridview.agent = s.agent
        s.rl_init()
        return s

    def readFile(self, filename):
        if filename is not None and filename != '':
            lst = readGridworld(filename)
            gridworld = self.genGridworld(lst)
            set_window_title_from_namestring(gridworld, filename)

    def writeFile(self, filename):
        olist = prepareWrite(self.gridview)
        olist['objects'] = strlist(self.gridview.objects)
        # str(self.gridview.objects)
        writeGridworld(olist, filename)

    @staticmethod
    def genGridworld(alist, agentclass=DynaGridAgent):
        (width, height, startsquare, goalsquare,
         barrierp, wallp) = getgwinfo(alist)
        squaresize = alist.get('squaresize')
        objects = alist.get('objects')
        gridworld = ObjectGridworldWindow(width, height, startsquare,
                                          goalsquare, squaresize)

        gridworld.environment = gridworld.gridview
        gridworld.agent = agentclass(numstates=gridworld.gridview.numsquares,
                                     numactions=gridworld.gridview.numactions())
        gridworld.rl_init()
        gridworld.gridview.agent = gridworld.agent

        if barrierp is not None:
            gridworld.gridview.barrierp = barrierp
        if wallp is not None:
            gridworld.gridview.wallp = wallp
        if objects is not None:
            gridworld.gridview.objects = objects
            gridworld.gridview.updatedisplay = True

        return gridworld

    @staticmethod
    def new_gridworld_from_file(filename):
        ObjectGridworldWindow.genGridworld(alist=readGridworld(gwFilename(filename)))

    def setObject(self):
        """toggle between clicks meaning barriers and clicks meaning objects"""
        if self.gridview.clickBarrier:
            self.setClickObject()
        else:
            self.setClickBarrier()

    def changeType(self):
        """toggle between permanent and consumable objects"""
        if self.gridview.curtype == 'permanent':
            self.gridview.curtype = 'consumable'
        else:
            self.gridview.curtype = 'permanent'
        gSetTitle(self.typebutton, self.gridview.curtype)

    def setClickBarrier(self):
        self.gridview.clickBarrier = True
        gSetTitle(self.addbutton, "Click means barrier")

    def setClickObject(self):
        self.gridview.clickBarrier = False
        gSetTitle(self.addbutton, "Click means object")

    def incrObjValue(self):
        self.gridview.curvalue += self.gridview.objIncr
        gSetTitle(self.valbutton, str(round(self.gridview.curvalue, 1)))

    def decrObjValue(self):
        self.gridview.curvalue -= self.gridview.objIncr
        gSetTitle(self.valbutton, str(round(self.gridview.curvalue, 1)))

    def resetObjLimits(self, low, high):
        self.gridview.lowObjValue = low
        self.gridview.Value = high

    def resetObjIncr(self, incr):
        self.gridview.objIncr = incr

    def addObjectMenu(self):
        omenu = gAddMenu(self, "Objects",
                         [["Click means Objects", self.setClickObject],
                          ["Click means Barriers", self.setClickBarrier],
                          ["Increment Object Value", self.incrObjValue],
                          ["Decrement Object Value", self.decrObjValue],
                          '---'])
        gAddMenu(omenu, "Set object value range",
                 [["Object values -1.0 to 1.0",
                   lambda: self.resetObjLimits(-1.0, 1.0)],
                  ["Object values -10.0 to 10.0",
                   lambda: self.resetObjLimits(-10.0, 10.0)],
                  ["Object values -100.0 to 100.0",
                   lambda: self.resetObjLimits(-100.0, 100.0)]])
        gAddMenu(omenu, "Set object value increment",
                 [["Increment/Decrement by 0.1",
                   lambda: self.resetObjIncr(0.1)],
                  ["Increment/Decrement by 1.0",
                   lambda: self.resetObjIncr(1.0)],
                  ["Increment/Decrement by 10.0",
                   lambda: self.resetObjIncr(10.0)]])

    def addGridworldMenu(self):
        m = gAddMenu(self, "Gridworld",
                     [
                         ['button', "Show Policy Arrows", self.showpolicyarrows,
                          1, 0,
                          lambda: self.toggleShowArrows()],
                         ['button', "Show Value Colors", self.showvaluecolors,
                          1, 0,
                          lambda: self.toggleShowColors()],
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
                                                             20)],
                  ["Maze single", lambda: ObjectGridworldWindow.new_gridworld_from_file(
                      'gw25x25maze_single')],
                  ["Maze", lambda: ObjectGridworldWindow.new_gridworld_from_file('gw25x25maze')],
                  ])


###

def makeObjectGridworldSimulation(w=16, h=16, st=0, g=1, size=30,
                                  agentclass=DynaGridAgent):
    s = ObjectGridworldWindow(width=w, height=h, startsquare=st, goalsquare=g,
                              squaresize=size)
    s.environment = s.gridview
    s.agent = agentclass(numstates=s.environment.numsquares,
                         numactions=s.environment.numactions())
    s.rl_init()
    s.gridview.agent = s.agent
    # return s