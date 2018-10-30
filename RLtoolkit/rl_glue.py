"""Glues together an experiment, agent, and environment.
"""

from abc import ABCMeta, abstractmethod


class RLGlue:
    """Facilitates interaction between an agent and environment for
    reinforcement learning experiments.

    args:
        env_obj: an object that implements BaseEnvironment
        agent_obj: an object that implements BaseAgent
    """

    def __init__(self, env_obj, agent_obj):
        self.environment = env_obj
        self.agent = agent_obj

        # useful statistics
        self.total_reward = None
        self.num_steps = None
        self.num_episodes = None
        self.num_ep_steps = None

        # the most recent state and action taken by the agent
        self.last_action = None
        self.last_state = None

    def rl_init(self):
        # reset statistics
        self.total_reward = 0
        self.num_steps = 0
        self.num_episodes = 0
        self.num_ep_steps = 0

        # reset last state and action
        self.last_action = None
        self.last_state = None

        # reset agent and environment
        self.agent.agent_init()
        self.environment.env_init()

    def rl_start(self):
        """Starts RLGlue experiment.

        Returns:
            tuple: (state, action)
        """
        self.num_ep_steps = 0

        self.last_state = self.environment.env_start()
        self.last_action = self.agent.agent_start(self.last_state)

        return self.last_state, self.last_action

    def rl_step(self):
        """Takes a step in the RLGlue experiment.

        Returns:
            (float, state, action, Boolean): reward, last state observation,
                last action, boolean indicating termination
        """
        a = self.last_action
        reward, self.last_state, terminal = self.environment.env_step(a)

        self.total_reward += reward

        if terminal:
            self.num_episodes += 1
            self.agent.agent_end(reward)
            self.last_action = None
        else:
            self.last_action = self.agent.agent_step(reward, self.last_state)

        self.num_ep_steps += 1
        self.num_steps += 1

        return reward, self.last_state, self.last_action, terminal

    ### CONVENIENCE FUNCTIONS BELOW ###
    def rl_env_start(self):
        """Useful when manually specifying agent actions (for debugging). Starts
        RL-Glue environment.

        Returns:
            state observation
        """
        self.num_ep_steps = 0
        self.last_state = self.environment.env_start()

        return self.last_state

    def rl_env_step(self, action):
        """Useful when manually specifying agent actions (for debugging).Takes a
        step in the environment based on an action.

        Args:
            action: Action taken by agent.

        Returns:
            (float, state, Boolean): reward, state observation, boolean
                indicating termination.
        """
        reward, self.last_state, terminal = self.environment.env_step(action)

        self.total_reward += reward

        if terminal:
            self.num_episodes += 1
        else:
            self.num_ep_steps += 1

        self.num_steps += 1

        return reward, self.last_state, terminal

    def rl_episode(self, max_steps_this_episode):
        """Convenience function to run an episode.

        Args:
            max_steps_this_episode (Int): Max number of steps in this episode.
                A value of 0 will result in the episode running until
                completion.

        """
        terminal = False

        self.rl_start()

        while not terminal and ((max_steps_this_episode == 0) or
                                (self.num_ep_steps < max_steps_this_episode)):
            _, _, _, terminal = self.rl_step()


class BaseAgent:
    """Implements the agent for an RL-Glue environment.
    Note:
        agent_init, agent_start, agent_step, and agent_end are required methods.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """Declare agent variables."""
        pass

    @abstractmethod
    def agent_init(self):
        """Initialize agent variables."""

    @abstractmethod
    def agent_start(self, state):
        """The first method called when the experiment starts, called after
        the environment starts.
        Args:
            state (state observation): The agent's current state

        Returns:
            The first action the agent takes.
        """

    @abstractmethod
    def agent_step(self, reward, state):
        """A step taken by the agent.
        Args:
            reward (float): the reward received for taking the last action taken
            state (state observation): The agent's current state
        Returns:
            The action the agent is taking.
        """

    @abstractmethod
    def agent_end(self, reward):
        """Run when the agent terminates.
        Args:
            reward (float): the reward the agent received for entering the
                terminal state.
        """


class BaseEnvironment:
    """Implements the environment for an RLGlue environment

    Note:
        agent_init, env_start, and env_step are required methods.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        """Declare environment variables."""

    @abstractmethod
    def env_init(self):
        """Initialize environment variables.

        Note:
            Initialize a tuple with the reward, first state observation,
            and a boolean indicating whether the state is terminal.
        """

    @abstractmethod
    def env_start(self):
        """The first method called when the experiment starts, called before the
        agent starts.

        Returns:
            The first state observation from the environment.
        """

    @abstractmethod
    def env_step(self, action):
        """A step taken by the environment.

        Args:
            action: The action taken by the agent

        Returns:
            (float, state, Boolean): a tuple of the reward, state observation,
                and boolean indicating if it's terminal.
        """
