from typing import Callable, List, Tuple, Iterator, Generator, Any, Iterable, Union
from itertools import product


def append_to_dict(d: dict, k:str, x: float):
    if x in d.keys():
        d[k].append(x)
    else:
        d[k] = [x]
    return d


def append_dict_to_dict(data: dict, d: dict):
    for k, v in d.items():
        data = append_to_dict(data, k, v)
    return data


def get_cartesian_product(*args):
    '''
    Cartesian product is the ordered set of all combinations of n sets
    '''
    return list(product(*args))


def zip_in_n_chunks(arg: Iterable[Any], n: int) -> zip:   
    return zip(*([iter(arg)]*n))


def test():
    import numpy as np
    arg = np.arange(0, 10)
    iterator = zip_in_n_chunks(arg, 2)
    for i, j in iterator:
        print(i, j)

flatten_lst_of_lst = lambda lst_of_lst: [lst for sublst in lst_of_lst for lst in sublst]

if __name__ == '__main__':

    test()


