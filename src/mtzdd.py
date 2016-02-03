#!/usr/bin/env python

import unittest, random, types

class MTZDD(object):
    def __init__(self):
        self.I = {}
        self.T = {}     # Terminal nodes. Map "node id" -> "value list"
        self.H = {}
        self.L = {}
        self.N = 0
        self.u0 = 1
        self.P = {}
        self._min = {}
        
    def Pa(self, node):
        return self.P[node]
    
    def addTNode(self, v, n = -1):
        if (n == -1):
            n = self.N + 1
        if (n > self.N):
            self.N = n

        assert(type(v) is list)
        
        self.T[n] = v
        return n
    
    def addINode(self, v, l, h, n = -1):
        if (n == -1):
            n = self.N + 1
        if (n > self.N):
            self.N = n

        self.I[n] = v
        self.H[n] = h
        self.L[n] = l
        if not n in self.P:
            self.P[n] = []
        if not h in self.P:
            self.P[h] = []
        if not l in self.P:
            self.P[l] = []
        self.P[h].append(n)
        self.P[l].append(n)
        return n
                    
    @classmethod
    def getExample(cls):
        r = MTZDD()
        
        r.addINode(1, 2, 3, 1)
        r.addINode(2, 4, 5, 2)
        r.addINode(2, 5, 6, 3)
        r.addINode(3, 7, 8, 4)
        r.addINode(4, 8, 9, 5)
        r.addINode(3, 9, 10, 6)
        r.addTNode([0, 0, 0, 0], 7)
        r.addTNode([1, 1, 1, 1], 8)
        r.addTNode([5, 5, 5, 5], 9)
        r.addTNode([7, 7, 7, 7], 10)
        
        return r
        
    @classmethod
    def getRandomRuleDecayDistribution(cls, agents, alpha, p):
        return MTZDD.getExample() ## TODO
    
    def __str__(self):
        r = ''

        for id, v in self.I.iteritems():
            if id == self.u0:
                r = str(id) + ' ' + str(v) + ' ' + str(self.L[id]) + ' ' + str(self.H[id]) + ' ' + r
            else:
                r += str(id) + ' ' + str(v) + ' ' + str(self.L[id]) + ' ' + str(self.H[id]) + ' '
        
        r += '0 '
        
        for id, v in self.T.iteritems():
            r += str(id) + ' '
            for w in v:
                r += str(w) + ' '
            r += '-1 '

        r += '0'

        return r

    @classmethod
    def fromString(cls, s):
        r = MTZDD()
        
        i = iter(map(int, s.split(' ')))

        n = i.next()        
        r.u0 = n
        while n != 0:
            v = i.next()
            l = i.next()
            h = i.next()
            r.addINode(v,l,h,n)
            n = i.next()
        
        n = i.next()
        while n != 0:
            w = []
            v = i.next()
            while v != -1:
                w.append(v)
                v = i.next()
            r.addTNode(w,n)
            n = i.next()
        
        return r
        
    def __eq__(self, r):
        return self.I == r.I and self.T == r.T and self.H == r.H and self.L == r.L and self.N == r.N and self.P == r.P


    def precompute(self):
        self._goals = {}
        self._GS = []
        self._nodes = {}
        self._A = set()
        
        for n in self.I:
            if not self.I[n] in self._nodes:
                self._nodes[self.I[n]] = []
            self._nodes[self.I[n]].append(n)
            self._A.add(self.I[n])

        _GS = []
        for t in self.T:
            self._goals[t] = []
            for n in self.min(t):
                self._goals[t].append([t, n])
                self._GS.append([t,n])
    
    def min(self, t):
        if t in self._min:
            return self._min[t]
            
        m = set()
        
        for n in self.Pa(t):
            if self.H[n] == t:
                s = set()
                s.add(n)
                m |= s
            else:
                m |= self.min(n)

        self._min[t] = m
        
        return m
    
    # Every goal is a pair [t, n]
    #   t - id of terminal node
    #   n - id of first node of high edge
    def goals(self, t):
        return self._goals[t]
    
    def GS(self):
        return self._GS
        
    def nodes(self, i):
        if not i in self._nodes:
            return []
        return self._nodes[i]

    def h(self, g):
        return [ g[1], self.H[g[1]] ]
    
    def A(self):
        return self._A
        
#
# Unit tests for the MTZDD class
#

class MTZDDTests(unittest.TestCase):
    def singleRuleSerializationTest(self, r):
        "Tests serialization to string and parsing of r"
        p = MTZDD.fromString(str(r))
        
        self.failUnless(r == p)

    def testSerialization(self):
        r = MTZDD.getExample()

        self.singleRuleSerializationTest(r)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
