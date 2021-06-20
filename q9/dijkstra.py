from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os
''' Add your imports here ... '''
import csv


#log = core.getLogger()
delayFile = "abilen_delay.csv"

''' Add your global variables here ... '''
delayFile = csv.DictReader(open(delayFile))

class Dijkstra (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        #log.debug("Enabling Dijkstra Module")
        self.thelist =  {}
        for row in delayFile:
            link = row["link"]
            delay = row["delay"]
            self.thelist[link] = delay
        print self.thelist
        # make a graph with all of the switches and their delay values
        graph = {'s1': {'h1': 1, 's2': self.thelist["A"] , 's3': self.thelist["N"]},
            's2': {'h2': 1, 's4': self.thelist["B"] , 's3': self.thelist["M"] },
            's4': {'h4': 1, 's5': self.thelist["C"] , 's10': self.thelist["I"] },
            's5': {'h5': 1, 's9': self.thelist["H"] , 's6': self.thelist["D"] },
            's6': {'h6': 1, 's7': self.thelist["E"] },
            's7': {'h7': 1, 's8': self.thelist["F"] },
            's8': {'h8': 1, 's9': self.thelist["G"] },
            's9': {'h9': 1, 's10': self.thelist["J"] },
            's10': {'h10': 1, 's11': self.thelist["K"] },
            's11': {'h11': 1, 's3': self.thelist["L"] },
            'h1': {'s1': 0},
            'h2': {'s2': 0},
            'h3': {'s3': 0},
            'h4': {'s4': 0},
            'h5': {'s5': 0},
            'h6': {'s6': 0},
            'h7': {'s7': 0},
            'h8': {'s8': 0},
            'h9': {'s9': 0},
            'h10': {'s10': 0},
            'h11': {'s11': 0},
            'h12': {'s12': 0},
            'h13': {'s13': 0},
            'h14': {'s14': 0},
            'h15': {'s15': 0},
            }

    # from http://geekly-yours.blogspot.com/2014/03/dijkstra-algorithm-python-example-source-code-shortest-path.html
    def dijkstra(graph,src,dest,visited=[],distances={},predecessors={}):
        """ calculates a shortest path tree routed in src
        """    
        # a few sanity checks
        if src not in graph:
            raise TypeError('the root of the shortest path tree cannot be found in the graph')
        if dest not in graph:
            raise TypeError('the target of the shortest path cannot be found in the graph')    
        # ending condition
        if src == dest:
            # We build the shortest path and display it
            path=[]
            pred=dest
            while pred != None:
                path.append(pred)
                pred=predecessors.get(pred,None)
            return path
        else :     
            # if it is the initial  run, initializes the cost
            if not visited: 
                distances[src]=0
            # visit the neighbors
            for neighbor in graph[src] :
                if neighbor not in visited:
                    new_distance = distances[src] + graph[src][neighbor]
                    if new_distance < distances.get(neighbor,float('inf')):
                        distances[neighbor] = new_distance
                        predecessors[neighbor] = src
            # mark as visited
            visited.append(src)
            # now that all neighbors have been visited: recurse                         
            # select the non visited node with lowest distance 'x'
            # run Dijskstra with src='x'
            unvisited={}
            for k in graph:
                if k not in visited:
                    unvisited[k] = distances.get(k,float('inf'))        
            x=min(unvisited, key=unvisited.get)
            dijkstra(graph,x,dest,visited,distances,predecessors)


    def _handle_ConnectionUp (self, event):    
        ''' Add your logic here ... '''
        # for every node in the graph, make the flows
        for node1 in graph.keys():
            for node in graph.keys():
                path = dijkstra(graph, node1, node2)
                # for every node in our path, create the flow to the next node in the path
                for link1 in path:
                    link2 = link1+1
                    for link2 in path:
                        fm = of.ofp_flow_mod()
                        fm.match.in_port = link1
                        fm.actions.append(of.ofp_action_output(port = link2))
        
        #log.debug("Dijkstra installed on %s", dpidToStr(event.dpid))        

def launch ():
    '''
    Starting the Dijkstra module
    '''
    core.registerNew(Dijkstra)
