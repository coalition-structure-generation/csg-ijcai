#!/usr/bin/env python

import argparse, sys, os, signal, time

parser = argparse.ArgumentParser()
parser.add_argument('--directory', help='output directory', action='store', default='experiments/')
parser.add_argument('--cores', type=int, help='number of parallel processes to run', default=1)
args = parser.parse_args()

directory = args.directory
cores = args.cores

print "\033[1;34mCSG Parallel Solver\033[0m"
print ""

if cores > 1:
    cores = 1
    print "  \033[1;33mWarning:\033[0m parallel computations not implemented, set cores=1"
    print ""

print "  Directory: \033[1;33m", directory, "\033[0m"
print "      Cores: \033[1;33m", cores, "\033[0m"

#
# SIGINT handling
#

interrupt_level = 0
def signal_handler(signal, frame):
    global interrupt_level
    
    interrupt_level = interrupt_level + 1

    print "User interrupt"

signal.signal(signal.SIGINT, signal_handler)

#
# TODO: parallelisation
#
        
while interrupt_level == 0:
    code = os.system('./csg_worker.py -q --directory ' + directory) / 256
        
    if code == 1:
        print "\n\033[1;34mComputation finished\033[0m"
        break
        
    if code == 2:
        print "\033[1;34mComputation interrupted by user\033[0m"
        break
        
    if code != 0:
        print "\033[1;34mAn error occured\033[0m"
        sys.exit(2)

