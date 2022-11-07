
# from typing import Callable
# int, float, str, dict, list, tuple since python 3.10+ 

from ast import literal_eval
import pprint

from walle.bureaucrat import DictToClass

from pathlib import Path
import numpy as np

# you can write here all possible input values
# TODO write a function that autoimports (or takes your list) and tests them all 

def get_test(path: str = None) -> DictToClass:
    
    project_name:   str         = 'string'   # wandb cfg
    entity:         int         = 1
    dtype:          float       = 'f32'
    exp_name:       Path        = 'junk'
    n_epoch:        np.ndarray     = 100
    
    c = locals()
    
    return 

if __name__ == '__main__':

    pass

