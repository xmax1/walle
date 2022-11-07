
from inspect import signature, Parameter
import numpy as np
from time import time


def robust_wrapper(fn):
    """ non-essential code wrapper: Allow core code to run with bugs in non-essential
    NB   @robust_wrapper(arg0=val, ..., ) potential in idea zone
    NB   otherwise uses defaults (predefined)
    EDU  nested wrappers https://stackoverflow.com/questions/30904486/python-wrapper-function-taking-arguments-inside-decorator """
    
    defaults = {
        float: 1.,
        str: 'word',
        int: 1,
        dict: {'word': 1},
        np.ndarray: np.array([1.])
    }

    args_for_fail = []
    for k, p in signature(fn).parameters.items():
        if p.default == Parameter.empty:
            args_for_fail.append(defaults[p.annotation])

    def new_fn(*args):
        try:
            out = fn(*args)
        except Exception as e:
            print(f'Error in {fn.__name__}', e)
            out = fn(*args_for_fail)
        return out 

    return new_fn     


def wprint():
    return


def wlog():
    return


def wtime():
    return        


@robust_wrapper
def track_time(
    step: int, 
    total_step: int, 
    t0: float, 
    every_n: int=10,
    tag: str = ''
):
    """ Prints time """
    if step % every_n == 0:
        d, t0 = time() - t0, time()
        print(
            f'{tag} | \
            % complete: {step/float(total_step):.2f} | \
            t: {(d):.2f} |'
        )
    return t0  # replaces t0 external


### TIMING ###
def track_time(
    step: int, 
    total_step: int, 
    t0: float, 
    every_n: int=10,
    tag: str=''
):
    """ Prints time
    
    """
    if step % every_n == 0:
        d, t0 = time() - t0, time()
        print(
            f'{tag} | \
            % complete: {step/float(total_step):.2f} | \
            t: {(d):.2f} |'
        )
    return t0  # replaces t0 external



def fuck_tensorflow():
    import tensorflow as tf
    tf.config.experimental.set_visible_devices([], "GPU")