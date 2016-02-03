#!/usr/bin/env python

class Constraint(object):
    LT = 1
    GT = 2
    EQ = 3
    
    def __init__(self):
        self.type = Constraint.LT
        self.bound = 0.0
        self.var = {}
    
    def addVariable(self, var, val):
        # TODO: check if var exists and adjust accordingly
        self.var[var] = val
    
    def setBound(self, val):
        self.bound = val
            
    def setType(self, type):
        assert(type == Constraint.LT or type == Constraint.GT or type == Constraint.EQ)
        self.type = type

    def __str__(self):
        s = ''
        
        first = True
        for var, val in self.var.iteritems():
            if not first:
                s += ' + '
            else:
                first = False
            s += str(val) + ' ' + var
            
        if self.type == Constraint.EQ:
            s += ' = '
        elif self.type == Constraint.LT:
            s += ' <= '
        elif self.type == Constraint.GT:
            s += ' >= '
            
        s += str(self.bound)
        
        return s
