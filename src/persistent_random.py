#!/usr/bin/env python

#
# Random numbers reproducible across different platforms and python versions
#
# Source:
#  http://stackoverflow.com/questions/23373777/pseudo-random-number-generation-in-python-without-using-modules-and-clock
#

class WichmannHill(object):
    def __init__(self, a=0):
        self.seed(a)

    def seed(self, a=None):
        a, x = divmod(a, 30268)
        a, y = divmod(a, 30306)
        a, z = divmod(a, 30322)
        self._seed = int(x)+1, int(y)+1, int(z)+1

    def random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        x, y, z = self._seed
        x = (171 * x) % 30269
        y = (172 * y) % 30307
        z = (170 * z) % 30323
        self._seed = x, y, z
        return (x/30269.0 + y/30307.0 + z/30323.0) % 1.0