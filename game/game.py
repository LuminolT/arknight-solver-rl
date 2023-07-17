'''
Author: LuminolT luminol.chen@gmail.com
Date: 2023-07-17 09:20:32
LastEditors: LuminolT luminol.chen@gmail.com
LastEditTime: 2023-07-17 10:56:30
FilePath: \arknight-solver-rl\game\game.py
Description: 

Copyright (c) 2023 by LuminolT, All Rights Reserved. 
'''
from random import sample
from typing import List
from collections import namedtuple

NextNode = namedtuple('NextNode', ['node', 'points'])
Action = namedtuple('Action', ['next_node', 'skill']) # skill is a int indicating the skill node
Observation = namedtuple('Observation', ['cur_node', 'points', 'done'])

class Game:
    
    def __init__(self) -> None:
        """initialize the game
        """
        # neighbors of each node
        #   [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, X]
        self._graph = [
            [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        
        _2_point_nodes_candidate = [3, 4, 5 ,6] # walk through these nodes get 2 points
        _3_point_nodes_candidate = [2, 7]       # walk through these nodes get 3 point
        
        # one way pairs
        self._one_way_pairs = [[4, 5], [6, 7]]
        self._one_way_pair_nodes = [item for pair in self._one_way_pairs for item in pair] # a helper list
        
        # randomize the game, update the graph
        self._randomize_game(_2_point_nodes_candidate, _3_point_nodes_candidate)
        
        # get the end nodes
        self._end_nodes = self._get_end_nodes()
        
        # game status
        self._skill_left = 1 # the skill left of the game
        self._cur_node   = 0 # the current node of the game
        self._steps      = 0 # the steps of the game
        self._points     = 0 # the points of the game
    
    def step(self, action: Action) -> Observation:
        """step the game
        """
        # check if the action is valid
        next_node, skill = action.next_node, action.skill
        if skill and self._skill_left > 0:
            self._skill_left -= 1
            self._use_skill(skill)
        
        if next_node not in self._get_next_nodes(self._cur_node):
            raise ValueError("Invalid next_node!")
        
        # update the game status
        self._steps += 1
        self._points += self._graph[self._cur_node][next_node]
        self._cur_node = next_node
        
        # check if node walk through the one way path
        if self._cur_node in self._one_way_pair_nodes:
            self._one_way_update(self._cur_node)
        
        # check if the game is over
        if self._cur_node in self._end_nodes:
            done = True
        else:
            done = False
            
        # return the observation
        return Observation(self._cur_node, self._points, done)
    
    def _use_skill(self, skill: int) -> None:
        """use the skill to trans the node to special node

        Args:
            skill (int): the target node
            
        Refs:
            - You can transform any specified node and two random nodes in the graph
                into 3 point nodes at any time
        """
        random_nodes_candidate = list(range(1, len(self._graph)))
        random_nodes_candidate.remove(skill)
        random_nodes = sample(random_nodes_candidate, 2)
        
        affected_nodes = [skill] + random_nodes
        
        # transform the affected nodes
        for out_degree in self._graph:
            for node in affected_nodes:
                out_degree[node] = 3 if out_degree[node] else 0        
    
    def _one_way_update(self, node: int) -> None:
        """the one way node update, once walk through these nodes, the pair node path will be blocked

        Args:
            node (int): the node to be updated
            
        Tips:
            - the one way nodes are defined in `self._one_way_pairs`
            - the update triggered after the agent's action
        
        Example:
            - if there is a pair `[4, 5]`, when the agent walk through 4 -> 5,
                then the path 5 -> 4 will be blocked
        """
        idx = self._one_way_pair_nodes.index(node)
        prev_node = idx ^ 1
        
        self._graph[node][prev_node] = 0
                
    def _get_end_nodes(self) -> List[int]:
        """get the end nodes of the graph

        Returns:
            List[int]: the end nodes of the graph
        """
        
        end_nodes = []
        for idx in range(len(self._graph)):
            # check if the node has no out-degree
            if not any(self._graph[idx]):
                end_nodes.append(idx)
        return end_nodes

    def get_next_nodes(self, cur_node: int) -> List[NextNode]:
        """get the next nodes of the current node

        Args:
            cur_node (int): the current node

        Returns:
            List[NextNode]: the next nodes of the current node
        """
        return [NextNode(node, value) for node, value in enumerate(self._graph[cur_node]) if value != 0]

    def _randomize_game(self, _2_point_nodes_candidate:List[int], _3_point_nodes_candidate:List[int]):
        """randomize the game, update the graph.
        """
        _2_point_nodes = sample(_2_point_nodes_candidate, 1)
        _3_point_nodes = sample(_3_point_nodes_candidate, 1)
        # _2_point_nodes.append(1)
        # _3_point_nodes.append(2)
        
        for out_degree in self._graph:
            for _2_point_node in _2_point_nodes:
                if out_degree[_2_point_node] == 1:
                    out_degree[_2_point_node] = 2
            for _3_point_node in _3_point_nodes:
                if out_degree[_3_point_node] == 1:
                    out_degree[_3_point_node] = 3
                    
    def _print_graph(self):
        """print the graph
        """
        for out_degree in self._graph:
            print(out_degree)