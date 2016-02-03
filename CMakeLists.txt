#
# Makefile generation for Non-Utilitarian CSG experiments
#
# To repeat experiments:
#
# > cd <project root>
# > mkdir build/
# > cd build/
# > cmake ..
# > make problems
# > make computations
# > make graphs
#
# The graphs, problems and byproducts of the computation will be saved to 
#   the subdirectory ${DIRECTORY} (default experiments/) in the project root
#
# The computation step can be interrupted (using SIGINT or Ctrl-C in the terminal)
#   and then restarted by reissuing command 'make computations'
# Warning: reissuing command 'make problems' will reset computation state
# You can modify CORES parameter to specify number of computations that are running
#   in parallel

project("Non-Utilitarian CSG")

#
# Default parameters (used to generate tables from the paper)
#

set(DIRECTORY ${PROJECT_SOURCE_DIR}/experiments)
set(CORES 2)

set(SEED 314159265)
set(AGENTS 100)
set(STEPS 10)
set(REPETITIONS 5)

set(DECAY_ALPHA 0.55)
set(DECAY_P     0.2)
set(TRI_P       0.2)
set(TRI_N       0.02)

#
# Version 2.8 required to be able to pass arguments to final make
#

CMAKE_MINIMUM_REQUIRED(VERSION 2.8 FATAL_ERROR)

#
# Unit tests. Usage: ... (TODO)
#

enable_testing()

#
# Copy the source files
#

add_subdirectory(src)

#
# Generation of problems
#

add_custom_target(problems
#  USES_TERMINAL
  COMMAND ./experiment_generator.py --seed ${SEED} --agents ${AGENTS} --steps ${STEPS} --repetitions ${REPETITIONS} --directory ${DIRECTORY}
    --decay_alpha ${DECAY_ALPHA} --decay_p ${DECAY_P} --tri_p ${TRI_P} --tri_n ${TRI_N}
  DEPENDS src/experiment_generator.py src/problem_generator.py src/mcnets_mip_generator.py
  WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
)

#
# Computations (this step can be stopped and restarted later)
#

add_custom_target(computations
#  USES_TERMINAL
  COMMAND ./parallel_solver.py --directory ${DIRECTORY} --cores ${CORES}
)

#
# Graph generation
#

add_custom_target(graphs
#  USES_TERMINAL
  COMMAND ./graph_generator.py --directory ${DIRECTORY}
)
