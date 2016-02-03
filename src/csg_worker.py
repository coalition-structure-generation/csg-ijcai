#!/usr/bin/env python

###
### SIGINT handling
###

from signal import signal, SIGINT, SIG_IGN
from sys import exit

def signal_handler(signal, frame):
    print "\n  \033[1;33mComputation interrupted by user.\033[0m\n"
    exit(2)

signal(SIGINT, signal_handler)

###

import argparse, os, sqlite3, time, gurobipy

###
### Command line arguments
###

parser = argparse.ArgumentParser()
parser.add_argument('--quiet', '-q', action='store_true')
parser.add_argument('--directory', help='output directory', action='store', default='experiments/')
args = parser.parse_args()

directory = args.directory + '/'

if not args.quiet:
    print "\033[1;34mCSG Single Instance Solver\033[0m"
    print ""
    print "   Directory: \033[1;33m", directory, "\033[0m"

#
# Connect to the database
#

conn = sqlite3.connect(directory + '/csg_problems.db')
conn.isolation_level = None
cur = conn.cursor()

#
# Fetch problem and mark as assigned
#

cur.execute("select * from problems where solved = 0 order by assigned limit 1")
row = cur.fetchone()

# Return -1 if there are no more problems left
if row is None:
    if not args.quiet:
        print "\n  \033[1;33mAll done!\033[0m\n"
    exit(1)

### TODO: set assigned to current timestamp

if not args.quiet:
    print "     Problem: \033[1;33m", row[0], "\033[0m"

cur.close()

###
### Computation
### 

# TODO: write log to appropriate file (not console)

start_time = time.time() * 1000.0
model = gurobipy.read(directory + row[8])
model.params.threads = 1
model.params.MIPfocus = 3
model.optimize()
elapsed_time = time.time() * 1000.0 - start_time

if model.Status == gurobipy.GRB.OPTIMAL:
    solution_type = 'FEASIBLE'
elif model.Status == gurobipy.GRB.INFEASIBLE:
    print "\033[1mError:\033[0m\033[1;31m model is INFEASIBLE.\033[0m"
    exit(3)    
elif model.Status == gurobipy.GRB.INF_OR_UNBD:
    print "\033[1mError:\033[0m\033[1;31m model is UNBOUNDED.\033[0m"
    exit(3)   
else:
    print "\n\033[1;33mComputation interrupted, terminating.\033[0m\n"
    exit(2)

solution_objective = model.ObjBound
solution_time = elapsed_time

###
### Save computation results
##

signal(SIGINT, SIG_IGN)
conn = sqlite3.connect(directory + '/csg_problems.db')
conn.isolation_level = None
cur = conn.cursor()
cur.execute('UPDATE problems SET solved=1, solution_time = %d, solution_objective = %f, solution_type = "%s" WHERE problem_id = "%s"' \
            % (solution_time, solution_objective, solution_type, row[0]))

cur.close()
