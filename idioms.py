from itertools import product


def zip_in_n_chunks(arg, n):
    return zip(iter(arg)*n)


def get_all_combinations(*args):
    return list(product(*args))
