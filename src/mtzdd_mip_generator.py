#!/usr/bin/env python

import argparse, sys
from mtzdd import MTZDD
from constraint import Constraint
        
###
### Command line arguments
###

parser = argparse.ArgumentParser()
parser.add_argument('--quiet', '-q', action='store_true')
parser.add_argument('input', default=sys.stdin, type=argparse.FileType('r'), 
                    nargs='?', help='input filename')
parser.add_argument('-o', '--output', default=sys.stdout, type=argparse.FileType('w'), 
                    nargs='?', help='output filename')
parser.add_argument('--type', default='egalitarian', choices=['egalitarian', 'balanced', 'utilitarian-tu'],
                    help='problem type')
args = parser.parse_args()

if not args.quiet:
    print "\033[1;34mCSG MIP Problem Generator for MTZDD Representation\033[0m"
    print ""
    print "           Input file: \033[1;33m", args.input.name, "\033[0m"
    print "          Output file: \033[1;33m", args.output.name, "\033[0m"
    print "         Problem type: \033[1;33m", args.type, "\033[0m"
    print ""


###
### Read input file
###

ifile = args.input
li = ifile.readline().strip()
while li.startswith("#") or li == '':
    li = ifile.readline().strip()
p = MTZDD.fromString(li)
ifile.close()

p.precompute()

###
### Generate constraints
###

constr = []
binary = set()

def xvar(g):
    global binary
    v = "x_" + str(g[0]) + "_" + str(g[1])
    binary.add(v)
    return  v

def xevar(g, e):
    global binary
    v = "xe_" + str(g[0]) + "_" + str(g[1]) + "_" + str(e[0]) + "_" + str(e[1])
    binary.add(v)
    return  v

#
# Constraints of type (i)
#

for g in p.GS():
    c = Constraint()
    c.addVariable(xvar(g), 1.0)
    c.addVariable(xevar(g, p.h(g)), -1.0)
    c.setType(Constraint.EQ)
    c.setBound(0.0)
    constr.append(c)

#
# Constraints of type (ii)
#

for t in p.T:
    zero = True
    for x in p.T[t]:
        if x != 0:
            zero = False
    if zero:
        continue
    for g in p.goals(t):
        c = Constraint()
        c.addVariable(xvar(g), 1.0)
        for u in p.Pa(t):
            c.addVariable(xevar(g, [ u, t ]), -1.0)
        c.setType(Constraint.EQ)
        c.setBound(0.0)
        constr.append(c)

#
# Constraints of type (iii)
#

for u in p.I:
    if u == p.u0:
        continue
    for g in p.GS():
        c = Constraint()        
        c.addVariable(xevar(g, [u, p.H[u]]), 1.0)
        c.addVariable(xevar(g, [u, p.L[u]]), 1.0)
        for up in p.Pa(u):
            c.addVariable(xevar(g, [up, u]), -1.0)
        c.setType(Constraint.EQ)
        c.setBound(0.0)
        constr.append(c)

#
# Constraints of type (iv)
#

for i in p.A():
    c = Constraint()

    for u in p.nodes(i):
        for g in p.GS():
            c.addVariable(xevar(g, [u, p.H[u]]), 1.0)
            
    c.setType(Constraint.LT)
    c.setBound(1.0)
    constr.append(c)
            
#
# Objective
#

def avar(x):
    return "a_" + str(x)
    
if args.type == 'egalitarian':
    obj = 'Maximize\n  obj: aMin'
    for a in p.A():
        c = Constraint()
        for g in p.GS():
            c.addVariable(xvar(g), p.T[g[0]][a-1])
        c.addVariable(avar(a), -1.0)
        c.setBound(0.0)
        c.setType(Constraint.EQ)
        constr.append(c)
    
        c = Constraint()
        c.addVariable("aMin", 1.0)
        c.addVariable(avar(a), -1.0)
        c.setBound(0.0)
        c.setType(Constraint.LT)
        constr.append(c)

elif args.type == 'balanced':
    obj = 'Minimize\n  obj: '
    # TODO

elif args.type == 'utilitarian-tu':
    obj = 'Maximize\n  obj: '
    first = True
    for g in p.GS():
        if not first:
            obj += ' + '
        else:
            first = False

        # For TU we take only the first component of the payout vector as the value        
        obj += str(p.T[g[0]][0]) + ' ' + xvar(g)
    obj += '\n'

###
### Write output
###
    
ofile = args.output

ofile.write(obj)
ofile.write("\n")
ofile.write("Subject To\n")

for c in constr:
    ofile.write(str(c) + '\n')

ofile.write("Binary\n")

for b in binary:
    ofile.write(b + '\n')
    
ofile.close()
