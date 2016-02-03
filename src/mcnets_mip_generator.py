#!/usr/bin/env python

import argparse, sys
from mcnets import MCNetsRule
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
parser.add_argument('--type', default='egalitarian', choices=['egalitarian', 'elitist'],
                    help='problem type')
args = parser.parse_args()

if not args.quiet:
    print "\033[1;34mCSG MIP Problem Generator for MC-Nets Representation\033[0m"
    print ""
    print "           Input file: \033[1;33m", args.input.name, "\033[0m"
    print "          Output file: \033[1;33m", args.output.name, "\033[0m"
    print "         Problem type: \033[1;33m", args.type, "\033[0m"
    print ""

###
### Read input file
###

ifile = args.input
rules = []
agents = set()

n = 1
for line in ifile:
    li=line.strip()
    if not li.startswith("#") and li != '':
        r = MCNetsRule.fromString(li)
        r.no = n
        n = n + 1
        agents |= r.P
        agents |= r.N
        for a in r.V:
            agents.add(a)

        rules.append(r)

if not args.quiet:
    print "Read %d rules with %d agents." % (len(rules), len(agents))

###
### Generate constraints
###

constr = []

#
# Part I. Feasible rule sets.
#

n_cs = 0
n_cd = 0
n_ic = 0
n_id = 0

def xvar(r):
    return 'x_' + str(r.no)

def yvar(r, ri, rj):
    return 'y_' + str(r.no) + '_' + str(ri.no) + '_' + str(rj.no)

# we collect numbers of edges of type CS for faster computation
csedges = []
for r1 in rules:
    for r2 in rules:
        if MCNetsRule.CS(r1,r2):
            csedges.append([r1, r2])

for r1 in rules:
    for r2 in rules:
        if r1.no == r2.no:
            continue
    
        cnt = 0
        
        if MCNetsRule.IC(r1, r2):
            cnt = cnt + 1 
            n_ic = n_ic + 1
            
            c = Constraint()
            
            c.addVariable(xvar(r1), 1.0)
            c.addVariable(xvar(r2), 1.0)
            c.setType(Constraint.LT)
            c.setBound(1.0)
            
            constr.append(c)    # (17)
        
        if MCNetsRule.CS(r1,r2):
            cnt = cnt + 1 
            n_cs = n_cs + 1
            
        if MCNetsRule.CD(r1,r2):
            cnt = cnt + 1 
            n_cd = n_cd + 1
            
            if r2.no > r1.no:
                c = Constraint()
                c.addVariable(yvar(r1, r1, r2), 1.0)
                c.setType(Constraint.EQ)
                c.setBound(0.0)
                constr.append(c)    # (18)
                
                c = Constraint()
                c.addVariable(yvar(r2,r1,r2), 1.0)
                c.setType(Constraint.GT)
                c.setBound(1.0)
                constr.append(c)    # (19)
            
            for csedge in csedges:
                c = Constraint()
                c.addVariable(yvar(r1, csedge[0], csedge[1]), 1.0)
                c.addVariable(yvar(r2, csedge[0], csedge[1]), -1.0)
                c.addVariable(xvar(csedge[0]), 1.0)
                c.addVariable(xvar(csedge[1]), 1.0)
                c.setType(Constraint.LT)
                c.setBound(2.0)
                constr.append(c)    # (20)
                
                c = Constraint()
                c.addVariable(yvar(r1, csedge[0], csedge[1]), -1.0)
                c.addVariable(yvar(r2, csedge[0], csedge[1]), 1.0)
                c.addVariable(xvar(csedge[0]), 1.0)
                c.addVariable(xvar(csedge[1]), 1.0)
                c.setType(Constraint.LT)
                c.setBound(2.0)
                constr.append(c)    # (21)
                
        if MCNetsRule.ID(r1,r2):
            cnt = cnt + 1 
            n_id = n_id + 1

        assert(cnt == 1)    

#
# Part II. Agent payouts (NTU).
#

def avar(k):
    return 'a' + str(k)

for a in agents:
    c = Constraint()
    c.addVariable(avar(a), 1.0)
    
    for r in rules:
        if a in r.V:
            c.addVariable(xvar(r), -r.V[a])
    c.setType(Constraint.EQ)
    c.setBound(0.0)
    constr.append(c)

#
# Part III. Egalitarian problem
#

if args.type == 'egalitarian':
    for a in agents:
        c = Constraint()        
        c.addVariable('minA', 1.0)
        c.addVariable(avar(a), -1.0)
        c.setType(Constraint.LT)
        c.setBound(0.0)
        constr.append(c)

    obj = 'Maximize\n  obj: minA\n'

#
# Part V. Elitist problem
#

def wvar(k):
    return 'w' + str(k)

if args.type == 'elitist':
    for a in agents:
        c = Constraint()        
        c.addVariable('maxA', 1.0)
        c.addVariable(avar(a), -1.0)
        c.addVariable(wvar(a), -1000000.0)
        c.setType(Constraint.LT)
        c.setBound(0.0)
        constr.append(c)

    c = Constraint()
    for a in agents:
        c.addVariable(wvar(a), 1.0)
        c.setBound(1.0)
        c.setType(Constraint.EQ)
    constr.append(c)

    obj = 'Maximize\n  obj: maxA\n'
    
###
### Write output
###
    
ofile = args.output

if not args.quiet:
    print "Edge counts (directed): IC", n_ic, "CS", n_cs, "CD", n_cd, "ID", n_id
    print ""

ofile.write(obj)
ofile.write("\n")
ofile.write("Subject To\n")

for c in constr:
    ofile.write(str(c) + '\n')

ofile.write("Binary\n")

for r in rules:
    ofile.write(xvar(r) + '\n')

if args.type == 'elitist':
    for a in agents:
        ofile.write(wvar(str(a)) + '\n')

ofile.close()
