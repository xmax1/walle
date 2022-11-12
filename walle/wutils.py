
from difflib import get_close_matches
from typing import Any, Callable, Iterable
import sys
import numpy as np
from inspect import signature, Parameter
from time import time
from pathlib import Path

### UTILITY CLASSES ###
def is_array(x: Any):
    return ('shape' in dir(x))
    
class wClass():
    can_nest: bool = True

    @property
    def dict(self):
        return self.__dict__

    @property
    def wclass(self):
        return [k for k,v in self.dict.items() if isinstance(v, wClass)]

    def todict(self):
        return self.__dict__
    
    def values(self):
        return self.dict.keys()

    def keys(self):
        return self.dict.keys()

    def items(self):
        return self.dict.items()

    def get(self, k):
        return self.dict[k]

    def maybe_fudge_key(self, k: str):
        if k not in self.keys():
            print(f'Finding closest match for name {k} getter, lil buggy bug boop')
            match = get_close_matches(k, self.keys(), n=1, cutoff=0.5)[0]  # returns list, 
            print(f'Guessing {(k := match)} for key attempt {k}')
        return k

    def __getattr__(self, k: str) -> Any:
        if k in self.keys():
            return self.dict[k]
        else:
            name = self.wclass([k in c for c in self.wclass].index(True))
            return self.dict[name].dict[k]

    def __init__(self, **kwarg):
        super().__init__()
        for k,v in kwarg.items():
            setattr(self, k, v)


class Cfg(wClass):
    def __init__(self, d: dict):
        super().__init__()

        for k,v in d.items():
            setattr(self, k, v)

    def __setattr__(self, k: str, v: Any):
        if is_array(v):
            v = np.array(v)
        self.dict[k] = v

class Stats(wClass):
    """ collects things """
    
    def __init__(self):
        super().__init__()

    def __setattr__(self, k: str, v: Any) -> None:
        v = np.array(v).tolist()
        
        if k not in self.keys():
            self.dict[k] = []
        
        self.dict[k] += [v]

        # what does exp_stat.x = 100 call first?
        # what does exp_stat.x += 100 call first?

    def __getattr__(self, k: str) -> Any:
        return np.array(self.dict[k])

    def set_by_name(self, k, v):
        self.__setattr__(k, v)

    def process(self, names: str | list, fn: Callable):
        if isinstance(names, str):
            names = [names]
        
        for name in names:
            self.dict[name] = np.array(fn(self.dict[name]))

    def overwrite(self, k, v):
        self.d[k] = np.array(v)

### SAFE_UTILS ###

defaults = {
    float: 1.,
    str: 'word',
    int: 1,
    dict: {'word': 1},
    bool: True,
    np.ndarray: np.array([1.]), 
    Path: Path('./tmp/_wfail').mkdir(parents=True, exist_ok=True),
    tuple: (1, 2, 3,)
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
        print(arg)
        kwarg = {k:ty_d[k](a) for k,a in kwarg.items()}
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

### BETA ###

# @wfail
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

def wtest():
    """ prints all the info of a variable in the local scope at exit
    https://stackoverflow.com/questions/3850261/doing-something-before-program-exit """

    def new_fn():
        __start_ = set(globals())



        __end_   = set(globals()) - __start_
    return  

class persistent_locals(object):
    def __init__(self, func):
        # https://code.activestate.com/recipes/577283-decorator-to-expose-local-variables-of-a-function-/
        self._locals = {}
        self.func = func
        self._run = 0

    def __call__(self, *args, **kwargs):
        if self._run:
            def tracer(frame, event, arg):
                if event=='return':
                    self._locals = frame.f_locals.copy()

            sys.setprofile(tracer) # tracer is activated on next call, return or exception
            try: # trace the function call
                res = self.func(*args, **kwargs)
            finally: # disable tracer and replace with old one
                sys.setprofile(None)
        else:
            res = self.func(*args, **kwargs)
        return res 

    def clear_locals(self):
        self._locals = {}

    @property
    def locals(self):
        return self._locals


def statsCollect(var, var_all=[]):
    var_all += [var]   


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