
import numpy as np

from random import sample
from typing import List
from collections import namedtuple

NextNode = namedtuple('NextNode', ['node', 'points'])
Action = namedtuple('Action', ['next_node', 'skill']) # skill is a int indicating the skill node
Observation = namedtuple('Observation', ['cur_node', 'points', 'done'])

class QTable:
    
    def __init__(self, graph_size=11, alpha=0.1, gamma=0.9) -> None:
        """ initialize the q table

        Args:
            graph_size (int, optional): Defaults to 11.
            alpha (float, optional): Defaults to 0.1.
            gamma (float, optional): Defaults to 0.9.
            
        Tips:
            - actions 
        """
        self._table = np.zeros((graph_size, graph_size, 2)) # 2 for skill or not
        self._alpha = alpha
        self._gamma = gamma
    
    @property
    def epsilon(self, num_episode: int):
        """epsilon
        """
        return 20. / (num_episode + 100) if num_episode is not None else 0.2
    
    def take_action(self, cur_node: int, num_episode: int) -> Action:
        rand_percent = np.random.uniform(0, 1)
        if rand_percent < self.epsilon(num_episode):
            # random action
            return self._random_action(cur_node)
        else:
            # greedy action
            return self._greedy_action(cur_node)