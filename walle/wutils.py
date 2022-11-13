
from typing import Any
import numpy as np

### UTILITY CLASSES ###
def is_array(x: Any):
    return ('shape' in dir(x))
    
class SubClass:
    """
    %reset -f if testing in jupyter, because globals can only tell if a variable has CHANGED"""
    def __init__(self):
        pass
    def __enter__(self):
        self.__var = dict(globals())
        return self
    def __exit__(self, *args):
        _g = {k:v for k,v in dict(globals()).items() if not ((k in self.__var) or ('__' in k))}
        for k, v in _g.items():
            if not isinstance(v, SubClass):
                self.__dict__[k] = v

class wStats:
    """ collects things """
    data = {}
    def __init__(self, name):
        self.name = name
    def __setattr__(self, v: Any) -> None:
        v = np.array(v).tolist()
        self.data += [v]

class dumpData:
    def __init__(self, metrics):
        for m in metrics:
            setattr(self, m, wStats())

class SubClass:
    """
    %reset -f if testing in jupyter, because globals can only tell if a variable has CHANGED"""
    def __init__(self):
        pass
    def __enter__(self):
        self.__var = dict(globals())
        return self
    def __exit__(self, *args):
        _g = {k:v for k,v in dict(globals()).items() if not ((k in self.__var) or ('__' in k))}
        for k, v in _g.items():
            if not isinstance(v, SubClass):
                self.__dict__[k] = v