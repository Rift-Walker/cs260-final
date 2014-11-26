# You will implement this class
# At the minimum, you need to implement the selectNodes function
# If you override __init__ from the agent superclass, make sure that the interface remains identical as in agent; 
# otherwise your agent will fail

from agent import Agent
    
class MyAgent(Agent):

    def selectNodes(self, network, t):
        # select a subset of nodes (up to budget) to seed at current time step t
        # nodes in the network are selected *** BY THEIR INDEX ***

        selected = set() # this is compatible with [] and provides reasonably fast set operations.

        # your code goes here

        # initialize sets of influenced (covered) and uninfluenced (uncovered) nodes
        uncovered = set(range(network.size()))
        covered = set()

        for b in range(self.budget):
            maxsize = 0
            maxnode = -1
            maxset = set()

            for i in uncovered:
               iset = set(network.getNeighbors(i)) - selected
               isize = len(iset)

               if isize > maxsize:
                   maxsize = isize
                   maxnode = i
                   maxset = iset

            selected.add(maxnode)
            uncovered.remove(maxnode)
            covered.add(maxnode)
            uncovered -= maxset
            covered |= maxset

        return selected
        
    def display():
        print "Agent ID ", self.id

