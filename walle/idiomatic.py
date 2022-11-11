from typing import Any, Iterable
from itertools import product

def get_cartesian_product(*args):
    """ Cartesian product is the ordered set of all combinations of n sets """
    return list(product(*args))

def zip_in_n_chunks(arg: Iterable[Any], n: int) -> zip:   
    return zip(*([iter(arg)]*n))

def flat_list(lst_of_lst):
    return [lst for sublst in lst_of_lst for lst in sublst]

def test():
    import numpy as np
    arg = np.arange(0, 10)
    iterator = zip_in_n_chunks(arg, 2)
    for i, j in iterator:
        print(i, j)

if __name__ == '__main__':
    test()


