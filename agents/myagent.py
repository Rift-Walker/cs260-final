# You will implement this class
# At the minimum, you need to implement the selectNodes function
# If you override __init__ from the agent superclass, make sure that the interface remains identical as in agent; 
# otherwise your agent will fail

from agent import Agent
import copy
    
class MyAgent(Agent):

    def rec(self, network, unselected, covered, upperBound, budget):

        if budget == 0:
            return []
        #priority = sorted(unselected, key=lambda i: len(set([item for sublist in (map(network.getNeighbors, network.getNeighbors(i))) for item in sublist])), reverse=False)
        priority = sorted(unselected, key=lambda i: len(set(network.getNeighbors(i)) - covered), reverse=True)
        #priorities = map(lambda i: len(set(network.getNeighbors(i)) - covered), priority)
        #print(priorities)
        maxutil = 0
        maxret = []
        for i in xrange(2):
            pick = priority[i]
            irec = self.rec(network, \
                            unselected - set([pick]), \
                            covered | set([pick]) | set(network.getNeighbors(pick)), \
                            budget - 1) 
            iret = [pick] + irec
            #iutil = len(set([item for sublist in map(network.getNeighbors, iret) for item in sublist]) - covered)
            iutil = float(network.update(iret))
            if (iutil > maxutil):
                maxret = iret
                maxutil = iutil
            network.reverse()
                
        return maxret

     def greedy(self, network):

        # python's built in sets provide reasonably fast and easy to write set operations.
        selected = set()
        # initialize sets of unselected and already-covered nodes
        unselected = set(range(network.size()))
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

                if isize > maxsize 
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

        bound = network.update(self.greedy(network))
        network.reverse()
        ret = self.rec(network, set(range(network.size())), set(), bound, self.budget)
        print(ret)
        return ret

       
   
    def display():
        print "Agent ID ", self.id

