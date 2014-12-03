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
        self.nbrdict = {x: frozenset(self.network.getNeighbors(x) + [x]) for x in range(network.size())}
        self.scoredict = {x: len(self.nbrdict.get(x)) for x in range(network.size())}
        self.prioritylist = sorted(self.scoredict.items(), key=operator.itemgetter(1), reverse=True)
    
    def getBound(self, bound, selected, budget):
        budget -= len(selected) if selected else 0
        itr = (x for x in self.prioritylist if x[0] > (selected[-1] if selected else 0))
        for i in range(budget):
            bound -= next(itr)[1]
        return bound

    def remove(self, uncovered, node):
        return uncovered - self.nbrdict.get(node)

    def size(self):
        return self.network.size()

    def neighbors(self, node):
        return 
   
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
                iset = set(network.getNeighbors(i)) - covered
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

        networkdata = NetworkData(network)
        solution = self.greedy(network)
        globalbound = network.size() - network.update(solution)
        network.reverse()
        tasks = PriorityQueue()
        tasks.put((0, [], frozenset(range(network.size()))))

        while not tasks.empty():
            task = tasks.get()
            node = task[1]
            for i in range((node[-1] + 1 if node else 0), networkdata.size() - self.budget + (len(node) if node else 0) + 1):
                newnode = node + [i]
                newset = networkdata.remove(task[2], i)
                upperbound = len(newset)
                if len(newnode) == self.budget and upperbound < globalbound:
                    globalbound = upperbound
                    solution = newnode
                    continue
                lowerbound = networkdata.getBound(upperbound, newnode, self.budget)
                if lowerbound < globalbound:
                    tasks.put((upperbound, newnode, newset))
       
        print solution
        return solution
   
    def display():
        print "Agent ID ", self.id
