#!/usr/bin/env python

import unittest, sets, random

class MCNetsRule(object):
    def __init__(self):
        self.V = {}
        self.P = set()
        self.N = set()
        self.no = -1    # -1 is unset
        
    # agent no must be positive
    def addP(self, agent):
        assert(agent > 0)
        self.P.add(agent)
    
    def removeP(self, agent):
        assert(agent > 0)
        self.P.remove(agent)
        
    # agent no must be positive
    def addN(self, agent):
        assert(agent > 0)
        self.N.add(agent)
    
    def addV(self, agent, utility):
        assert(agent > 0)
        self.V[agent] = utility
        
        for x in range(agent - 1):
            if not (x+1) in self.V:
                self.V[x+1] = 0
                
    @classmethod
    def IC(cls, r1, r2):
         return bool(r1.P & r2.P) and (bool(r1.P & r2.N) or bool(r1.N & r2.P))

    @classmethod
    def CS(cls, r1, r2):
        return bool(r1.P & r2.P) and not bool(r1.P & r2.N) and not bool(r1.N & r2.P)
    
    @classmethod
    def CD(cls, r1, r2):
        return not bool(r1.P & r2.P) and (bool(r1.P & r2.N)  or bool(r1.N & r2.P))
        
    @classmethod
    def ID(cls, r1, r2):
        return not bool(r1.P & r2.P) and not bool(r1.P & r2.N) and not bool(r1.N & r2.P)
        
    @classmethod
    def fromString(cls, s):
        "Initialize from string"
        r = MCNetsRule()
        
        i = iter(map(int, s.split(' ')))
        
        x = i.next()
        while x != 0:
            if x < 0:
                r.addN(-x)
            else:
                r.addP(x)
            x = i.next()

        a = 1
        x = i.next()
        while x >= 0:
            r.addV(a, x)
            a = a + 1
            x = i.next()

        return r
    
    @classmethod
    def getRandomRuleTrinomialDistribution(cls, agents, probP, probN):
        r = MCNetsRule()
        
        for a in range(agents):
            dice = random.uniform(0.0, 1.0)
                        
            if dice <= probP:
                r.addP(a + 1)
                r.addV(a+1, random.randint(0, agents))
            elif dice <= probP + probN:
                r.addN(a + 1)
                r.addV(a+1, 0)
            else:
                r.addV(a+1, random.randint(0, agents))
            
        return r

    @classmethod
    def getRandomRuleDecayDistribution(cls, agents, alpha, p):
        r = MCNetsRule()
        
        a = range(agents)
        t = 0.0        
        
        while t < alpha and len(a) > 0:
            x = random.randint(0, len(a) - 1)
            
            t = random.uniform(0.0, 1.0)
            if t < p:
                r.addN(a[x] + 1)
            else:
                r.addP(a[x] + 1)

            a.remove(a[x])

            t = random.uniform(0.0, 1.0)
        
        for a in range(agents):
            if not a + 1 in r.N:
                r.addV(a + 1, random.randint(0, agents))
            else:
                r.addV(a + 1, 0)
                
        return r
            
    def __str__(self):
        r = ''
        m = 0
                
        for agent in self.P:
            r += str(agent) + ' '
            if agent > m:
                m = agent
                
        for agent in self.N:
            r += str(-agent) + ' '
            if agent > m:
                m = agent
        
        for agent in self.V:
            if agent > m:
                m = agent

        r += '0 '
        
        for a in range(m):
            if not (a+1) in self.V:
                r += '0 '
            else:
                r += str(self.V[a+1]) + ' '
        
        r += '-1'
        
        return r
    
    def __eq__(self, r):
        return r.P == self.P and r.N == self.N and r.V == self.V
        
#
# Unit tests for the MCNetRule class
#

class MCNetsRuleTests(unittest.TestCase):
    def singleRuleSerializationTest(self, r):
        "Tests serialization to string and parsing of r"
        p = MCNetsRule.fromString(str(r))
        
        self.failUnless(r == p)
    
    def testSerialization(self):
        "Test a specific rule"
        r = MCNetsRule()
        r.addP(3)
        r.addV(3, 5)
        r.addP(5)
        r.addP(7)
        r.addV(7, 17)
        r.addN(6)
        r.addN(4)

        self.singleRuleSerializationTest(r)

        "Test empty rule"
        r = MCNetsRule()
        self.singleRuleSerializationTest(r)
        
        "Test random rules"
        for n in range(100):
            r = MCNetsRule.getRandomRuleDecayDistribution(n, 0.55, 0.2)
            self.singleRuleSerializationTest(r)
                
def main():
    unittest.main()

if __name__ == '__main__':
    main()
