
from difflib import get_close_matches
from typing import Any, Callable, Iterable, TextIO
import numpy as np

### UTILITY CLASSES ###
class wClass():

    @property
    def d(self):
        return self.__dict__

    def keys(self):
        return self.d.keys()

    def items(self):
        return self.d.items()

    def get(self, k):
        return self.d[k]

    def maybe_fudge_key(self, k: str):
        if k not in self.keys():
            print(f'Finding closest match for name {k} getter, maybe you have a lil buggy bug boop')
            match = get_close_matches(k, self.keys(), n=1, cutoff=0.5)[0]  # returns list, 
            print(f'Guessing {(k := match)} for key attempt {k}')
        return k

    def __getattr__(self, k: str) -> Any:
        k = self.maybe_fudge_key(k)
        return self.d[k]
    
class Config(wClass):
    
    def __init__(self, d: dict):
        super().__init__()

        for k, v in d.items():
            setattr(self, k, v)

    def __setattr__(self, k: str, v: Any):
        self.d[k] = v

class Stats(wClass):
    
    def __init__(self):
        super().__init__()

    def __setattr__(self, k: str, v: int | float | Iterable) -> None:
        
        v = np.array(v)
        
        if v.ndim == 0: 
            v = v[None]

        if k not in self.keys():
            self.d[k] = v
        else:
            self.d[k] = np.concatenate([self.d[k], v], axis=0)

    def set_by_name(self, k, v):
        self.__setattr__(k, v)

    def process(self, names: str | list, fn: Callable):
        if isinstance(names, str):
            self.d[names] = np.array(fn(self.d[names]))
        else:
            for name in names:
                self.d[name] = np.array(fn(self.d[name]))

    def overwrite(self, k, v):
        self.d[k] = np.array(v)



from inspect import signature, Parameter
import numpy as np
from typing import Callable, Any
from time import time
from pathlib import Path
from bureaucrat import mkdir

defaults = {
    float: 1.,
    str: 'word',
    int: 1,
    dict: {'word': 1},
    bool: True,
    np.ndarray: np.array([1.]), 
    Path: mkdir(Path('./tmp'))
}

def wfail(fn):
    """ non-essential code wrapper: Allow core code to run with bugs in non-essential
    NB   @robust_wrapper(arg0=val, ..., ) potential in idea zone
    NB   otherwise uses defaults (predefined)
    EDU  nested wrappers https://stackoverflow.com/questions/30904486/python-wrapper-function-taking-arguments-inside-decorator """
    
    args_for_fail = []
    for name, arg in signature(fn).parameters.items():
        if arg.default == Parameter.empty:
            args_for_fail.append(defaults[arg.annotation])

    def new_fn(*args):
        try:
            out = fn(*args)
        except Exception as e:
            print(f'Error in {fn.__name__}', e)
            out = fn(*args_for_fail)
        return out 
    return new_fn 

""" SIGNATURE """
def wtype(fn: Callable):
    """     applies types from type hints to inputs 
    NB!!    NO WORKY fns with no types """
    ty_d = fn.__annotations__  # dict of args and types 
    ty = list(fn.__annotations__.values())
    def fn_with_typed_inputs(*arg, **kwarg):
        arg = [t(a) for t, a in zip(ty, arg)] 
        kwarg = [ty_d[k](a) for k, a in kwarg.items()] 
        return fn(*arg, **kwarg)
    return fn_with_typed_inputs

def wprint_dict(d: dict, name: str = None):
    if name is not None: print(f'dict: {name}')
    for key, kwa in d.items():
        wprint(kwa, name=key)

def var_info(v: Any):
    info = f' | type: {type(v)}'
    info += ' | shape: ' + (str(v.shape) if 'shape' in dir(v) else '()')
    return info

@wfail
def wprint(*arg: tuple, name: str=None, **kwarg):
    """
    NB  name for the recursion loop and used at the bottom of the tree (the arg)"""
    for i, a in enumerate(arg):
        arg_name = 'pos_arg'+str(i) if name is None else name
        if isinstance(arg, dict):
            wprint_dict(arg)
        else:
            # captures int, float, str, list, tuple, arrays, ... idk what missing
            print(f'{arg_name} = {a} ' +  var_info(a))

    wprint_dict(kwarg)
    return arg, kwarg

def wlog():
    return

def wtime():
    return        

@wfail
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



def fuck_tensorflow():
    import tensorflow as tf
    tf.config.experimental.set_visible_devices([], "GPU")