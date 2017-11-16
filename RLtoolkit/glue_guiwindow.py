import time

from RLtoolkit.g import *
from RLtoolkit.rl_glue import RLGlue


class SimulationWindow(Gwindow, RLGlue):
    def __init__(self, wwidth=500, wheight=600):
        if sys.platform in ['mac', 'darwin']:
            # account for menu being added to window in Windows and Linux
            extrah = 30
        else:
            extrah = 50
        Gwindow.__init__(self, windowTitle="Simulation Window",
                         gdViewportR=(0, 20, wwidth, wheight + extrah))
        RLGlue.__init__(self, env_obj=None, agent_obj=None)
        self.simulationrunning = False
        self.updatedisplay = True
        self.displaypause = 0
        self.redrawinterval = 1
        self.countsx = self.countsy = 0  # xcoord and ycoord of time displays
        self.lastcount = None
        self.dcount = 0  # display counter
        self.status = Gview(self)
        self.goff = gColorOff(self)
        gdSetViewportR(self.status, 0, wheight, wwidth, 30)
        self.gobutton = gdAddButton(self.status, "Go  ", self.sim_stop_go, 5, 0,
                                    self.goff)
        self.stepbutton = gdAddButton(self.status, "Step", self.single_step, 65,
                                      0, self.goff)
        self.episodebutton = gdAddButton(self.status, "Episode",
                                         self.single_episode, 125, 0, self.goff)
        if wwidth < 350:  # make the window longer and add the buttons there
            gdSetViewportR(self.status, 0, wheight, wwidth, 60)
            self.fastbutton = gdAddButton(self.status, "Faster ",
                                          self.sim_faster, 5, 30, self.goff)
            gdAddButton(self.status, "Slower", self.sim_slower, 80, 30,
                        self.goff)
        else:  # add the buttons horizontally
            self.fastbutton = gdAddButton(self.status, "Faster ",
                                          self.sim_faster, 210, 0, self.goff)
            gdAddButton(self.status, "Slower", self.sim_slower, 285, 0,
                        self.goff)
        self.debug = gIntVar()
        self.debug.set(0)
        self.setup_time_display()
        self.add_file_menu()
        self.add_simulation_menu()
        self.readtitle = "Open File"
        self.writetitle = "Save File As"
        self.initialdir = None

        # self.whole_view = self.whole_view
        # self.sim_stop_go = self.sim_stop_go
        # self.single_step = self.single_step
        # self.single_episode = self.single_episode
        # self.sim_faster = self.sim_faster
        # self.sim_slower = self.sim_slower
        # self.sim_display = self.sim_display

    def gDrawView(self):
        if self.updatedisplay:
            self.update_sim_display()
        self.sim_display_counts()
        gMakeVisible(self)

    def gKeyEventHandler(self, key):
        print(("got key", key))

    def whole_view(self):
        self.dcount = 0
        self.whole_sim_display()
        self.sim_display_counts()
        gMakeVisible(self)

    def simstep(self):
        if self.simulationrunning:
            # do a number of steps at once for speed
            for _ in range(self.redrawinterval):
                _, _, _, term = self.rl_step()
                if term:
                    self.rl_start()
            self.sim_display()
            gCheckEvents(self, self.simstep)
            # self.after(1, self.simstep)
            # using tk method after to force it to check for stop event

    def sim_stop_go(self):
        if self.simulationrunning:  # already running, stop it
            self.simulationrunning = False  # setSimulationRunning(self, False)
            gButtonEnable(self.stepbutton)
            gButtonEnable(self.episodebutton)
            gSetTitle(self.gobutton, "Go  ")
            self.whole_view()
        else:  # set it running
            self.simulationrunning = True  # setSimulationRunning(self, True)
            gButtonDisable(self.stepbutton)
            gButtonDisable(self.episodebutton)
            gSetTitle(self.gobutton, "Stop")
            gMakeVisible(self)
            self.rl_start()
            self.simstep()

    def single_step(self):
        self.rl_step()
        self.whole_view()

    def epstep(self):
        if self.simulationrunning:
            # one step at a time - must check for episode termination
            _, _, _, terminal = self.rl_step()
            self.sim_display()
            if not terminal:  # end of episode
                gCheckEvents(self, self.epstep)
                # self.after(1, self.epstep)
                # using tk method after to force it to check for stop event
            else:
                self.sim_stop_go()  # reset buttons on display

    def single_episode(self):
        if not self.simulationrunning:
            gButtonDisable(self.stepbutton)
            gButtonDisable(self.episodebutton)
            gSetTitle(self.gobutton, "Stop")
            self.simulationrunning = True
            self.rl_start()  # force start of episode
            self.epstep()

    def sim_faster(self):
        if self.displaypause == 0:
            gSetTitle(self.fastbutton, "Jumpier")
            self.redrawinterval = 2 * self.redrawinterval
            if self.redrawinterval > 32:
                self.updatedisplay = False
        elif self.displaypause <= 0.01:
            self.displaypause = 0
            gSetTitle(self.fastbutton, "Faster ")
            self.redrawinterval = 1
        else:
            self.displaypause = self.displaypause / 2

    def sim_slower(self):
        if self.displaypause > 0:
            self.updatedisplay = True
            self.displaypause = max(0.01, 2 * self.displaypause)
        elif self.redrawinterval == 1:
            self.updatedisplay = True
            gSetTitle(self.fastbutton, "Faster ")
            self.displaypause = 0.01
        else:
            self.updatedisplay = True
            self.redrawinterval = self.redrawinterval // 2
            if self.redrawinterval == 1:
                gSetTitle(self.fastbutton, "Faster ")

    def sim_display(self):
        self.dcount += 1
        pause(self.displaypause)
        if (self.redrawinterval is not None and
                self.dcount % self.redrawinterval == 0):
            self.gDrawView()

    def gDestroy(self, event):
        global GDEVICE
        Gwindow.gDestroy(self, event)
        if not GDEVICE.childwindows:
            self.quit()

    def exit(self):
        gQuit()

    def setup_time_display(self):
        oldx1, oldy1, oldx2, oldy2, oldcorner = gGetCS(self.status)
        self.countsy = 10
        self.countsx = self.wwidth - 60

    def sim_display_counts(self):
        # Note: the specific application must update the stepnum, episodenum
        # and episodestepnum !!!
        if self.countsx is not None:
            if self.lastcount is not None:
                gDelete(self.status, self.lastcount)
            countstr = ("{}|{}|{}".format(self.num_steps,
                                          self.num_episodes,
                                          self.num_ep_steps))
            self.lastcount = gdDrawTextCentered(self.status, countstr,
                                                ("Chicago", 12, "normal"),
                                                self.countsx, self.countsy, gOn)

    def whole_sim_display(self):
        """display routine to redraw entire display - should be specified for
        each application
        """
        pass

    def update_sim_display(self):
        """update routine for display - should be specialized for each
        application
        """
        pass

    def open_file(self):
        """open simulation file"""
        filename = gOpenFileUserPick(None,
                                     title=self.readtitle,
                                     initialdir=self.initialdir)
        self.read_file(filename)

    def read_file(self, filename):
        """open file - should be specialized for each
        application
        """
        print("File not read - there is no readFile method")
        pass

    def save_file(self):
        """save currently open file"""
        filename = filename_from_title(self.title)
        if filename is not None and filename != "":
            self.write_file(filename)
        else:
            self.save_file_as()
        pass

    def save_file_as(self):
        """save current simulation as"""
        filename = gSaveFileUserPick(self,
                                     title=self.writetitle,
                                     initialdir=self.initialdir)
        if filename is not None and filename != '':  # not cancelled
            self.write_file(filename)
            set_window_title_from_namestring(self, filename)

    def write_file(self, filename):
        """save current simulation info - should be specialized for each
        application
        """
        print("File not saved - there is no writeFile method")
        pass

    def print_info(self):
        "print simulation info - should be specialized for each application"
        pass

    def reset_simulation(self):
        "reset simulation - should be specialized for each application"
        pass

    def add_simulation_menu(self):
        gAddMenu(self, "Simulation",
                 [["Start/Stop simulation", self.sim_stop_go],
                  ["Step simulation", self.single_step],
                  ["Simulate one episode", self.single_episode],
                  ["Faster ", self.sim_faster],
                  ["Slower", self.sim_slower],
                  '---',
                  ["Redisplay", self.gDrawView],
                  ["Redisplay All", self.whole_view],
                  '---',
                  ["Reset Simulation", self.reset_simulation],
                  # '---',
                # ['button', "Debug Mode", self.debug, 1, 0, self.toggleDebug],
                  ])

    def add_file_menu(self):
        gAddMenu(self, "File",
                 [["Open ...", self.open_file],
                  ["Save", self.save_file],
                  ["Save As ...", self.save_file_as],
                  ["Print", self.print_info],
                  ["Quit", self.exit]])


def pause(seconds):
    time.sleep(seconds)


def filename_from_title(title):
    position = title.find('-')
    if position is not None and position != -1:
        name = title[:position]
        path = title[position + 1:]
        filename = path + '/' + name
        filename = filename.strip()
        return filename


def set_window_title_from_namestring(window, filename):
    if isinstance(window, Gwindow):
        position = filename.rfind('/')
        if position is None or position == -1:
            newtitle = filename
        else:
            newtitle = filename[position + 1:] + ' - ' + filename[:position]
        window.title = newtitle
        gSetTitle(window, newtitle)
