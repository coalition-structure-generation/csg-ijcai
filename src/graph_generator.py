#!/usr/bin/env python

import argparse, sys, os, sqlite3

###
### Command line
###

parser = argparse.ArgumentParser()
parser.add_argument('--quiet', '-q', action='store_true')
parser.add_argument('--directory', help='output directory', action='store', default='../experiments')
args = parser.parse_args()

directory = args.directory + '/'

if not args.quiet:
    print "\033[1;34mGraph Generator\033[0m"
    print ""
    print "   Directory: \033[1;33m", directory, "\033[0m"

###
### Connect to the database
###

conn = sqlite3.connect(directory + '/csg_problems.db')
conn.isolation_level = None

###
### Enable math extensions
###

#conn.enable_load_extension(True)
#conn.load_extension("src/libsqlite_math.so")

cur = conn.cursor()

###
### Read data
###

cur.execute('select test_id, avg(solution_time), agents from problems where solved=1 group by agents, test_id')

rows = cur.fetchall()

###
### Create tables
### 

graphs = {}

for r in rows:
    if not r[0] in graphs:
        graphs[r[0]] = []
    
    graphs[r[0]].append([r[2], r[1]])
        
###
### Write tables
###

for name, table in graphs.iteritems():
    filename = name + '.dat'
    
    dat = open(directory + filename, 'w')
    dat.write('agents\ttime\n')
    for d in table:
        dat.write("%d\t%d\n" % (d[0],d[1]))

