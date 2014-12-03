# You will implement this class
# At the minimum, you need to implement the selectNodes function
# If you override __init__ from the agent superclass, make sure that the interface remains identical as in agent; 
# otherwise your agent will fail

from agent import Agent
import copy
import operator
import threading
from Queue import PriorityQueue


class NetworkData:
    def __init__(self, network):
        self.network = network
        # dictionary mapping nodes to their sets of neighbors (neighbor set includes selected node)
        self.nbrdict = {x: frozenset(self.network.getNeighbors(x) + [x]) for x in range(network.size())}
        # dictionary mapping nodes to their degrees
        self.scoredict = {x: len(self.nbrdict.get(x)) for x in range(network.size())}
        # nodes sorted by degree
        self.prioritylist = sorted(self.scoredict.items(), key=operator.itemgetter(1), reverse=True)
    
    # return upper bound for lower bound according to remaining budget. bound is calculated on a lower bound
    # (the calculated utility of a partial assignment) by adding to it the highest degrees of available nodes.
    def getBound(self, bound, selected, budget):
        # get remaining budget
        budget -= len(selected) if selected else 0
        # worst case, we add the top nodes and they have nothing in common.
        itr = (x for x in self.prioritylist if x[0] > (selected[-1] if selected else 0))
        for i in range(budget):
            bound += next(itr)[1]
        return bound

    # return new covered set given existing set and node
    def add(self, covered, node):
        return covered | self.nbrdict.get(node)

    # return size of network
    def size(self):
        return self.network.size()

    # return number of neighbors of a node
    def getNeighbors(self, node):
        return self.nbrdict.get(node)
   
class MyAgent(Agent):

    def greedy(self, network):

        # python's built in sets provide reasonably fast and easy to write set operations.
        selected = set()
        # initialize sets of unselected and already-covered nodes
        unselected = range(network.size())
        covered = set()

        # loop selecting one node at each iteration (up to a budget)
        for b in range(self.budget):
            maxsize = 0
            maxnode = -1
            maxset = set()
 
            # greedily choose a node maximizing number of neighbors not currently covered
            for i in unselected:
                iset = network.getNeighbors(i) - covered
                isize = len(iset)

                if isize > maxsize:
                    maxsize = isize
                    maxnode = i
                    maxset = iset

            # move node from unselected to selected list
            selected.add(maxnode)
            unselected.remove(maxnode)

            # mark selected node and its neighbors as covered
            covered.add(maxnode)
            covered |= maxset

            # it's worth noting that we don't remove the selected node's neighbors from the unselected set.
            # this allows some covered nodes to be possible future selections

        # return a list to maintain consistency with skeleton code (although returning the set also works)
        return list(selected)
 
    def selectNodes(self, network, t):
        # select a subset of nodes (up to budget) to seed at current time step t
        # nodes in the network are selected *** BY THEIR INDEX ***

        # fast data structures for network info and associated methods
        networkdata = NetworkData(network)

        # calculate an initial upper bound based on approximation algorithm
        solution = self.greedy(networkdata)
        globalbound = network.update(solution)
        network.reverse()

        # initialize priority queue of nodes
        tasks = PriorityQueue()
        # each node contains a priority (lower bound, negative becuase of the sort order)
        # , as well as as some assignment of variables and its coverd set
        tasks.put((0, [], frozenset()))

        while not tasks.empty():
            task = tasks.get()
            node = task[1]
            # branch...
            for i in range((node[-1] + 1 if node else 0), networkdata.size() - self.budget + (len(node) if node else 0) + 1):
                newnode = node + [i]
                newset = networkdata.add(task[2], i)
                lowerbound = len(newset)
                # check leaf nodes against current solution
                if len(newnode) == self.budget and lowerbound > globalbound:
                    globalbound = lowerbound
                    solution = newnode
                    continue
                # ...and bound.
                upperbound = networkdata.getBound(lowerbound, newnode, self.budget)
                if upperbound > globalbound:
                    # we pass along the set of covered nodes as we build it up
                    # alternatively, we could pass along the set of uncovered nodes, but that performs worse on smaller problems.
                    tasks.put((-lowerbound, newnode, newset))
       
        # search space exhausted. return best solution
        return solution
   
    def display():
        print "Agent ID ", self.id
