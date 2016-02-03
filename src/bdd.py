#!/usr/bin/env python

import random, argparse, sys
from mtzdd import MTZDD

parser = argparse.ArgumentParser()
parser.add_argument('output', default=sys.stdout, type=argparse.FileType('w'), 
                    nargs='?', help='output filename')
parser.add_argument('--agents', type=int, help='number of agents', default = 60)
parser.add_argument('--alpha', type=float, help='alpha', default = 0.55)
parser.add_argument('--seed', type=int, help='random seed', default=1)
args = parser.parse_args()

random.seed(args.seed)

def zero(list):
    for z in list:
        if z != 0:
            return False
    return True
            
class Node(object):
    uniq = {}
    cache = {}
    T = False
    idMax = 0
    
    def pathValue(self, p):        
        if self.T:
            if len(p) == 0:
                return self.v
            else:
                return None

        if len(p) == 0:
            return self.l.pathValue(p)
        
        if self.t > p[0]:
            return None
        
        if p[0] == self.t:
            return self.h.pathValue(p[1:])
        else:
            return self.l.pathValue(p)
            
    def __init__(self, t, l, h):
        self.t=t
        self.h=h
        self.l=l
        Node.idMax = Node.idMax + 1
        self.id = Node.idMax
        
    def __str__(self):
        return '(' + str(self.id) + '/' + str(self.t) + ') L' + str(self.l) + ' H' + str(self.h)
         
    def __hash__(self):
        if not self.T:
            return str(self.t) + "_" + self.l.__hash__() + "_" + self.h.__hash__()
        else:
            assert(False)

    @classmethod
    def hash(cls, t, P0, P1):
        return str(t) + "_" + P0.__hash__() + "_" + P1.__hash__()

    @classmethod
    def getnode(cls, t, P0, P1):
        if (P1.T and zero(P1.v)):
            return P0
        
        if Node.hash(t, P0, P1) in Node.uniq:
            return Node.uniq[Node.hash(t, P0, P1)]
                
        P = Node(t, P0, P1)
        
        Node.uniq[P.__hash__()] = P
        return P
        
    @classmethod 
    def union(cls, P, Q):
        if P.T and zero(P.v):
            return Q
        
        if P == Q or (Q.T and zero(Q.v)):
            return P

        assert(not (P.T and Q.T and not zero(P.v) and not zero(Q.v)) )
        
        if str(P) + 'U' + str(Q) in Node.cache:
            return Node.cache[str(P) + 'U' + str(Q)]
        
        if not P.T and (Q.T or P.t < Q.t):
            R = Node.getnode(P.t, Node.union(P.l, Q), P.h)
        elif not Q.T and (P.T or Q.t < P.t):
            R = Node.getnode(Q.t, Node.union(P, Q.l), Q.h)
        else:
            R = Node.getnode(P.t, Node.union(P.l, Q.l), Node.union(P.h, Q.h))

        Node.cache[str(P) + 'U' + str(Q)] = R
        
        return R
                
class Terminal(Node):
    T = True
    
    def __init__(self, v):
        self.v = v
        Node.idMax = Node.idMax + 1
        self.id = Node.idMax
        Node.uniq[self.__hash__()] = self

    def __str__(self):
        return '[' + str(self.v) + ']'

    def __hash__(self):
        return str(self)

t = []
for x in range(10):
    p = []
    for x in range(args.agents):
        p.append(random.randint(1,10))
    t.append(Terminal(p))

t0 = []
for x in range(args.agents):
    t0.append(0)
t0 = Terminal(t0)

def randomSCG(agents, alpha):
    scg = []
    a = range(agents)
    while len(a) > 0:
        x = a[random.randint(0,len(a)-1)] + 1
        scg.append(x)
        a.remove(x-1)
        if random.uniform(0.0, 1.0) > alpha:
            break

    scg.sort()
    return scg
    
def init_mtzdd(mtzdd, bdd):
    mtzdd.u0 = bdd.id
    _init_mtzdd(mtzdd,bdd)
        
def _init_mtzdd(mtzdd, bdd):
    if bdd.T:
        mtzdd.addTNode(bdd.v, bdd.id)
    else:
        mtzdd.addINode(bdd.t, bdd.l.id, bdd.h.id, bdd.id)
        _init_mtzdd(mtzdd, bdd.l)
        _init_mtzdd(mtzdd, bdd.h)

def randomBDDRule(agents, alpha):
    global t0, t
                    
    u = t0
    for a in range(agents):
        scg = randomSCG(agents, alpha)
        if u.pathValue(scg) is None:
            n = t[random.randint(0, 9)]
            scg.sort(reverse=True)
            for x in scg:
                n = Node.getnode(x, t0, n)

            u = Node.union(u, n)
#            print "appended " + str(scg)
        else:
            pass
#            print "skipped " + str(scg)
    
    m = MTZDD()
    init_mtzdd(m, u)
    m.precompute()
    return m
    
m = randomBDDRule(args.agents, args.alpha)

ofile = args.output
ofile.write(str(m))
ofile.write("\n")
ofile.close()
