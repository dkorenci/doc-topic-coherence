import os
from multiprocessing import cpu_count

import psutil


def unpinProcess():
    '''
    Set current process affinities (attachment to particular cores) to all cores.
    '''
    p = psutil.Process(os.getpid())
    p.cpu_affinity(range(cpu_count()))