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
        #self.nbrdict = {x: frozenset(network.getNeighbors(x)) for x in range(network.size())}
        self.degreedict = {x: network.degree(x) for x in range(network.size())}
        self.prioritylist = sorted(self.degreedict.items(), key=operator.itemgetter(1))
    
    def getBound(self, item, budget):
        bound = item[0] 
        selected = item[1]
        last = -1
        if selected:
            last = selected[-1]
            budget -= len(selected)
        avail = (budget - (len(selected if selected else 0)))
        for i in range(avail):
            best = next(x for x in self.prioritylist if x[0] > last and x[0] <= len(self.degreedict) - avail + i)
            last = best[0]
            bound += best[1]
        return bound
    
class RWLock:
    def __init__(self):
        self.write = threading.Semaphore(1)
        self.mutex = threading.Semaphore(1)
        self.readcount = 0

    def acquireWrite(self):
        self.write.acquire()

    def releaseWrite(self):
        self.write.release()

    def acquireRead(self):
        self.mutex.acquire()
        self.readcount += 1
        if self.readcount == 1:
            self.write.acquire()
        self.mutex.release()

    def releaseRead(self):
        self.mutex.acquire()
        self.readcount -= 1
        if self.readcount == 0:
            self.write.release()
        self.mutex.release()

class Mutable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class Worker(threading.Thread):

    def __init__(self, tasks, network, lock, solution, maxutil, networkdata, budget):
        threading.Thread.__init__(self)
        self.tasks = tasks
        self.network = network
        self.lock = lock
        self.solution = solution
        self.maxutil = maxutil
        self.networkdata = networkdata
        self.budget = budget
        self.daemon = True
        self.start()

    def run(self):
        while not self.tasks.empty():
            item = self.tasks.get()
            task = item[1]
            if len(task) == self.budget:
                util = self.network.update(task)
                self.network.reverse()
                leaf = True
                self.lock.acquireRead()
                if util > self.maxutil.get():
                    self.lock.releaseRead()
                    self.lock.acquireWrite()
                    if util > self.maxutil.get():
                        self.maxutil.set(util)
                        self.solution.set(task)
                    self.lock.releaseWrite()
                else:
                    self.lock.releaseRead()
            else:
                for i in range((task[-1] if task else 0), self.network.size() - self.budget + (len(task) if task else 0) + 1):
                    newnode = task + [i]
                    newitem = (self.network.update(newnode), newnode)
                    self.network.reverse()
                    upperbound = self.networkdata.getBound(newitem, self.budget)
                    self.lock.acquireRead()
                    if upperbound > self.maxutil.get():
                        self.tasks.put(newitem)
                    self.lock.releaseRead()
                    

   
class MyAgent(Agent):

    NUM_THREADS = 8 

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

        #solution = Mutable(self.greedy(network))
        solution = Mutable([])
        #bound = Mutable(network.update(solution.get()))
        bound = Mutable(0)
        network.reverse()
        tasks = PriorityQueue()
        tasks.put((0, []))
        lock = RWLock()
        
        threads = []
        for i in range(self.NUM_THREADS):
            threads.append(Worker(tasks, copy.deepcopy(network), lock, solution, bound, NetworkData(network), self.budget))
        for t in threads:
            t.join()
        print solution.get()
        return solution.get()

       
   
    def display():
        print "Agent ID ", self.id
