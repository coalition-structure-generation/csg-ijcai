#
# Makefile generation for Non-Utilitarian CSG experiments
#

configure_file(mcnets.py .. COPYONLY)
configure_file(mtzdd.py .. COPYONLY)
configure_file(constraint.py .. COPYONLY)
configure_file(experiment_generator.py .. COPYONLY)
configure_file(problem_generator.py .. COPYONLY)
configure_file(mcnets_mip_generator.py .. COPYONLY)
configure_file(mtzdd_mip_generator.py .. COPYONLY)
configure_file(parallel_solver.py .. COPYONLY)
configure_file(csg_worker.py .. COPYONLY)
configure_file(graph_generator.py .. COPYONLY)
configure_file(bdd.py .. COPYONLY)

add_test(mcnets ../mcnets.py)
add_test(mtzdd ../mtzdd.py)

add_library(sqlite_math MODULE extension-functions.c)
