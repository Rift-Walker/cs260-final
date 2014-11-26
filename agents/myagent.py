# You will implement this class
# At the minimum, you need to implement the selectNodes function
# If you override __init__ from the agent superclass, make sure that the interface remains identical as in agent; 
# otherwise your agent will fail

from agent import Agent
    
class MyAgent(Agent):

    def selectNodes(self, network, t):
        # select a subset of nodes (up to budget) to seed at current time step t
        # nodes in the network are selected *** BY THEIR INDEX ***

        # your code goes here
        uncovered = set(range(network.size()))
        recruited = set()
        covered = set()

        for b in range(self.budget):
            maxsize = 0
            maxnode = -1
            maxset = set()

            for i in uncovered:
               iset = set(network.getNeighbors(i)) - covered
               isize = len(iset)

               if isize > maxsize:
                   maxsize = isize
                   maxnode = i
                   maxset = iset

            recruited.add(maxnode)
            uncovered.remove(maxnode)
            covered.add(maxnode)
            uncovered -= maxset
            covered |= maxset

        return recruited
        
    def display():
        print "Agent ID ", self.id

