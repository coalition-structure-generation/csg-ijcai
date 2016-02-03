#!/usr/bin/env python

###
### SIGINT handling
###

from signal import signal, SIGINT
from sys import exit
import os

def signal_handler(signal, frame):
    print "  \033[1;33mProblem generation interrupted by user.\033[0m"
    exit(-2)

signal(SIGINT, signal_handler)

###

import sys, argparse, random
from mcnets import MCNetsRule
from mtzdd import MTZDD

#
# Generate a compact .mcn, .mtzdd or .scg representation of characteristic function
# for non-utilitarian csg, using one of the following methods.
#
# 1. Decay distribution, [1, p. 13]
# 2. ...
#
# References
# 
# 1. "Compact Representation Scheme ... ", Y. Sakurai et al
#


###
### Command line arguments
###

# format, output file, 
#   number of agents, number of rules, generation method (decay, ...)

parser = argparse.ArgumentParser()
parser.add_argument('--quiet', '-q', action='store_true')
parser.add_argument('-o', '--output', default=sys.stdout, type=argparse.FileType('w'), 
                    nargs='?', help='output filename')
parser.add_argument('--format', default='mcn', choices=['mcn', 'mtzdd'],
                    help='output format')
parser.add_argument('--agents', '-na', type=int, help='number of agents', default=50)
parser.add_argument('--rules', '-nr', type=int, help='number of rules', default=1)
parser.add_argument('--method', '-m', choices=['decay', 'trinomial'], help='method of generation',
                    default='trinomial')
parser.add_argument('--seed', type=int, help='random seed', default=1)
parser.add_argument('params', type=float, help='parameters specific to generation method', nargs='*')

args = parser.parse_args()

if (not args.quiet):
    print "\033[1;34mCSG Problem Generator\033[0m"
    print ""
    print "          Output file: \033[1;33m", args.output.name, "\033[0m"
    print "          File format: \033[1;33m", args.format, "\033[0m"
    print "     Number of agents: \033[1;33m", args.agents, "\033[0m"
    print "      Number of rules: \033[1;33m", args.rules, "\033[0m"
    print " Method of generation: \033[1;33m", args.method, "\033[0m"
    print "          Random seed: \033[1;33m", args.seed, "\033[0m"
    print ""

###
### Parameter checking
###

if args.format == 'mtzdd' and args.rules > 1:
    print "\033[1mError:\033[0m\033[1;31m mtzdd file format allows only single rule.\033[0m"
    sys.exit(2)

if args.format == 'mtzdd' and args.method != 'decay':
    print "\033[1mError:\033[0m\033[1;31m mtzdd implements only decay method.\033[0m"
    sys.exit(2)

if args.method == 'trinomial':
    if len(args.params) != 2:
        print "\033[1mError:\033[0m\033[1;31m trinomial method requires two arguments: P probability and N probability.\033[0m"
        sys.exit(2)

if args.method == 'decay':
    if len(args.params) != 2:
        print "\033[1mError:\033[0m\033[1;31m decay method requires two arguments: alpha probability and p probability.\033[0m"
        sys.exit(2)
        
random.seed(args.seed)

###
### Rule list generation
###

rules = []

for a in range(args.rules):

    if args.format == 'mcn':
        if args.method == 'trinomial':
            probP = args.params[0]
            probN = args.params[1]
            maxUtility = args.agents
            
            r = MCNetsRule.getRandomRuleTrinomialDistribution(args.agents, probP, probN)
        elif args.method == 'decay':
            decay_alpha = args.params[0]
            decay_p = args.params[1]
    
            r = MCNetsRule.getRandomRuleDecayDistribution(args.agents, decay_alpha, decay_p)
        else:
            pass

    if args.format == 'mtzdd':
        if args.method == 'decay':
            decay_alpha = args.params[0]
            decay_p = args.params[1]
            if args.output.name == '<stdout>':
                os.system('./bdd.py --agents ' + str(args.agents) + ' --alpha ' + str(decay_alpha) + ' --seed ' + str(args.seed))
            else:
                os.system('./bdd.py --agents ' + str(args.agents) + ' --alpha ' + str(decay_alpha) + ' --seed ' + str(args.seed) + ' ' + args.output.name)
            
            sys.exit(0)
                        
    rules.append(r)
        
###
### File generation
###

ofile = args.output

ofile.write("# Method: %s. Paremeters: %s. Agents: %d. Rules: %d. Random seed: %d.\n\n" % 
            (args.method, str(args.params), args.agents, args.rules, args.seed))

for r in rules:
    ofile.write(str(r) + '\n')

ofile.close()
