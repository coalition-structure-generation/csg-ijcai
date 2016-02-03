#!/usr/bin/env python

import argparse, sys, sqlite3, os, random

parser = argparse.ArgumentParser()
parser.add_argument('--directory', help='output directory', action='store', default='experiments/')
parser.add_argument('--seed', type=int, help='random seed', default=314159265)
parser.add_argument('--agents', type=int, help='number of agents', default = 60)
parser.add_argument('--steps', type=int, help='number of steps', default = 5)
parser.add_argument('--repetitions', type=int, help='number of repetitions', default=3)
parser.add_argument('--decay_alpha', type=float, default=0.55)
parser.add_argument('--decay_p', type=float, default=0.2)
parser.add_argument('--tri_p', type=float, default=0.2)
parser.add_argument('--tri_n', type=float, default=0.02)

args = parser.parse_args()

print "\033[1;34mCSG Experiment Generator\033[0m"
print ""
print "      Output directory: \033[1;33m", args.directory, "\033[0m"
print "      Number of agents: \033[1;33m", args.agents, "\033[0m"
print "       Number of steps: \033[1;33m", args.steps, "\033[0m"
print " Number of repetitions: \033[1;33m", args.repetitions, "\033[0m"
print "           Random seed: \033[1;33m", args.seed, "\033[0m"
print ""

decay_alpha = args.decay_alpha
decay_p = args.decay_p
tri_p = args.tri_p
tri_n = args.tri_n

#
# Create SQLite database
#

directory = args.directory
if not os.path.exists(directory):
    os.makedirs(directory)

#
# Table structure:
#
#   problem_id -- string (generated from number of agents and repetition number)
#   problem_type -- mcn or mtzdd
#   problem_file -- usually problem_id.problem_type
#   agents -- number of agents, 
#   parameters -- all other relevant generator parameters,
#   assigned -- assignment timestamp
#   solved -- boolean
#   solution_time -- solution time in milliseconds, 
#   solution_type -- feasible / error, 
#   solution_objective -- computed objective
#

conn = sqlite3.connect(directory + '/csg_problems.db')
conn.isolation_level = None
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS problems')

cur.execute('CREATE TABLE problems (\
    problem_id VARCHAR(64), \
    test_id VARCHAR(64), \
    problem_type VARCHAR(16), \
    problem_file VARCHAR(64), \
    agents INTEGER, \
    rules INTEGER, \
    seed INTEGER, \
    parameters VARCHAR(128), \
    mip_file VARCHAR(64), \
    mip_parameters VARCHAR(128), \
    assigned TIMESTAMP, \
    solved BOOLEAN, \
    solution_time INTEGER, \
    solution_type VARCHAR(32), \
    solution_objective FLOAT \
  )'
  )

###
### MC-Nets with decay or trinomial distribution (egalitarian and elitist)
###

def mcnets_generator(method, goal, a, i):
    global decay_alpha, decay_, tri_p, tri_n, cur
    
    test_id = 'mcn-'+method+'-'+goal+'-ntu'
    problem_id = 'mcn_' + str(a) + '_' + str(i + 1) + '_' + method + '_' + goal
    problem_type = 'mcn'
    problem_file = 'mcn_' + str(a) + '_' + str(i + 1) + '_' + method + '.' + problem_type
    agents = a
    rules = a
    seed = random.randint(0, 999999999)
    parameters = '--format mcn --agents ' + str(agents) + ' --rules ' + str(rules) + \
                 ' --seed ' + str(seed) + \
                 ' --output ' + directory + '/' + problem_file
    
    if method == 'decay':
        parameters += ' --method decay ' + str(decay_alpha) + ' ' + str(decay_p)
    elif method == 'trinomial':
        parameters += ' --method trinomial ' + str(tri_p) + ' ' + str(tri_n)

    #
    # Generate MCN problem file
    #
    cmd = './problem_generator.py -q ' + parameters
    code = os.system(cmd)
    if (code != 0):
        print "\033[1mError:\033[0m\033[1;31m Execution of command '" + cmd + "' failed.\033[0m"
        sys.exit(2)

    #
    # Generate MCN MIP file
    #
    mip_file = problem_id + '.lp'
    mip_parameters = directory + '/' + problem_file + \
                     ' --output ' + directory + '/' + mip_file + \
                     ' --type ' + goal
    cmd = './mcnets_mip_generator.py -q ' + mip_parameters
    code = os.system(cmd)
    if (code != 0):
        print "\033[1mError:\033[0m\033[1;31m Execution of command '" + cmd + "' failed.\033[0m"
        sys.exit(2)
        
    #
    # Insert database row with problem description
    #
    cur.execute('INSERT INTO problems VALUES ("%s", "%s", "%s", "%s", %d, %d, %d, "%s", "%s", "%s", NULL, 0, NULL, NULL, NULL)' 
        % (problem_id, test_id, problem_type, problem_file, agents, rules, seed, parameters, mip_file, mip_parameters))

###
### MTZDD with trinomial distribution (egalitarian, elitist and balanced)
###

def mtzdd_generator(goal, a, i):
    global decay_alpha, decay_, tri_p, tri_n, cur

    decay_alpha = 0.75
    
    test_id = 'mtzdd-decay-'+goal+'-ntu'
    problem_id = 'mtzdd_' + str(a) + '_' + str(i + 1) + '_decay_' + goal
    problem_type = 'mtzdd'
    problem_file = 'mtzdd_' + str(a) + '_' + str(i + 1) + '_decay.' + problem_type
    agents = a
    rules = 1
    seed = random.randint(0, 999999999)
    parameters = '--format mtzdd --agents ' + str(agents) + ' --rules 1' + \
                 ' --seed ' + str(seed) + \
                 ' --output ' + directory + '/' + problem_file + \
                 ' --method decay ' + str(decay_alpha) + ' ' + str(decay_p)

    #
    # Generate MTZDD problem file
    #
    cmd = './problem_generator.py -q ' + parameters
    code = os.system(cmd)
    if (code != 0):
        print "\033[1mError:\033[0m\033[1;31m Execution of command '" + cmd + "' failed.\033[0m"
        sys.exit(2)

    #
    # Generate MTZDD MIP file
    #
    mip_file = problem_id + '.lp'
    mip_parameters = directory + '/' + problem_file + \
                     ' --output ' + directory + '/' + mip_file + \
                     ' --type ' + goal
    cmd = './mtzdd_mip_generator.py -q ' + mip_parameters
    code = os.system(cmd)
    if (code != 0):
        print "\033[1mError:\033[0m\033[1;31m Execution of command '" + cmd + "' failed.\033[0m"
        sys.exit(2)

    #
    # Insert database row with problem description
    #
    cur.execute('INSERT INTO problems VALUES ("%s", "%s", "%s", "%s", %d, %d, %d, "%s", "%s", "%s", NULL, 0, NULL, NULL, NULL)' 
        % (problem_id, test_id, problem_type, problem_file, agents, rules, seed, parameters, mip_file, mip_parameters))

n = args.agents
s = args.steps
r = args.repetitions
n0 = n / s

for a in range(n0, n + 1, n0):
    print "  Generating %d problems with %d agents." % (r, a)
    for i in range(r):
        mcnets_generator('decay', 'egalitarian', a, i)
        # Not used in paper
        # mcnets_generator('decay', 'elitist', a, i)
        mcnets_generator('trinomial', 'egalitarian', a, i)
        # Not used in paper
        # mcnets_generator('trinomial', 'elitist', a, i)
        mtzdd_generator('egalitarian', a, i)
        # Not used in paper
        # mtzdd_generator('elitist', a, i)
        mtzdd_generator('balanced', a, i)
                   
#
# Save the database
#

cur.close()

#
#
#

print ""
print "\033[1;34mSuccess\033[0m"
