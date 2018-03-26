"""Glues together an experiment, agent, and environment.
"""

from __future__ import print_function

from abc import ABCMeta, abstractmethod


class RLGlue:
    """RLGlue class.

    args:
        env_obj: an object that implements BaseEnvironment
        agent_obj: an object that implements AgentEnvironment
    """

    def __init__(self, env_obj, agent_obj):
        self.environment = env_obj
        self.agent = agent_obj

        self.total_reward = None
        self.last_action = None
        self.num_steps = None
        self.num_episodes = None
        self.num_ep_steps = None

    def rl_init(self):
        self.total_reward = 0
        self.last_action = 0
        self.num_steps = 0
        self.num_episodes = 0
        self.num_ep_steps = 0

        self.agent.agent_init()
        self.environment.env_init()

    def rl_start(self):
        """Starts RLGlue experiment.

        Returns:
            tuple: (state, action)
        """
        self.num_ep_steps = 0

        last_state = self.environment.env_start()
        self.last_action = self.agent.agent_start(last_state)

        observation = (last_state, self.last_action)

        return observation

    def rl_env_start(self):
        """Useful when manually specifying agent actions (for debugging). Starts
        RL-Glue environment.

        Returns:
            (float, state, Boolean): reward, state observation, boolean
                indicating termination
        """
        self.total_reward = 0.0
        self.num_ep_steps = 1

        this_observation = self.environment.env_start()

        return this_observation

    def rl_env_step(self, action):
        """Useful when manually specifying agent actions (for debugging).Takes a
        step in the environment based on an action.

        Args:
            action: Action taken by agent.

        Returns:
            (float, state, Boolean): reward, state observation, boolean
                indicating termination.
        """
        ro = self.environment.env_step(action)
        (this_reward, _, terminal) = ro

        self.total_reward += this_reward

        if terminal:
            self.num_episodes += 1
        else:
            self.num_ep_steps += 1

        self.num_steps += 1

        return ro

    def rl_step(self):
        """Takes a step in the RLGlue experiment.

        Returns:
            (float, state, action, Boolean): reward, last state observation,
                last action, boolean indicating termination
        """
        (reward, state, term) = self.environment.env_step(self.last_action)

        self.total_reward += reward

        if term:
            self.num_episodes += 1
            self.agent.agent_end(reward)
            roat = (reward, state, None, term)
        else:
            self.last_action = self.agent.agent_step(reward, state)
            roat = (reward, state, self.last_action, term)

        self.num_ep_steps += 1
        self.num_steps += 1
        return roat

    def rl_episode(self, max_steps_this_episode):
        """Convenience function to run an episode.

        Args:
            max_steps_this_episode (Int): Max number of steps in this episode.
                A value of 0 will result in the episode running until
                completion.

        Returns:
            Boolean: if the episode should terminate
        """
        is_terminal = False

        self.rl_start()

        while (not is_terminal) and ((max_steps_this_episode == 0) or
                                     (self.num_steps < max_steps_this_episode)):
            rl_step_result = self.rl_step()
            is_terminal = rl_step_result[3]

        return is_terminal


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
    def agent_start(self, observation):
        """The first method called when the experiment starts, called after
        the environment starts.
        Args:
            observation (Numpy array): the state observation from the
                environment's evn_start function.
        Returns:
            The first action the agent takes.
        """

    @abstractmethod
    def agent_step(self, reward, observation):
        """A step taken by the agent.
        Args:
            reward (float): the reward received for taking the last action taken
            observation (Numpy array): the state observation from the
                environment's step based, where the agent ended up after the
                last step
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
        reward = None
        observation = None
        termination = None
        self.reward_obs_term = (reward, observation, termination)

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
