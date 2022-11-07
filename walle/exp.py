from typing import Any, Iterable, Callable
import sys
from ast import literal_eval
from difflib import get_close_matches
from pathlib import Path

import numpy as np

from bureaucrat import save_pk, load_pk, load_yaml, save_dict_as_yaml, join_and_mkdir

class BaseGet():
    
    def get(self, names: str | list, alternate: str | None = None) -> Any:
        
        if isinstance(names, str):
            names = self.check_and_fudge_key(names)
            return self.__dict__.get(names, alternate)

        new_names = []
        for name in names:
            name = self.check_and_fudge_key(name)
            new_names.append(name)

        return [self.__dict__.get(name, alternate) for name in new_names]

    def get_dict(self):
        return self.__dict__
    
    def to_dict(self):
        return self.__dict__

    def __getattr__(self, __key: str) -> Any:
        __key = self.check_and_fudge_key(__key)
        return self.__dict__.get(__key)

    def check_and_fudge_key(self, key):
        keys = self.__dict__.keys()
        if key not in keys:
            print(f'Finding closest match for name {key} getter, maybe you have a lil buggy bug boop')
            matches = get_close_matches(key, keys, n=1, cutoff=0.5)
            if len(matches) > 0:
                match = matches[0]
                print(f'Guessing {match} for key attempt {key}')
            else:
                match = 'THIS_KEY_DOES_NOT_EXIST'
            return match
        return key



class StatsCollector(BaseGet):
    def __init__(self):
        super().__init__()

    def __setattr__(self, __name: str, __value: int | float | Iterable) -> None:
        
        __value = np.array(__value)
        
        if __value.ndim == 0: 
            __value = __value[None]

        if __name not in self.__dict__.keys():
            self.__dict__[__name] = __value
        else:
            self.__dict__[__name] = np.concatenate([self.__dict__[__name], __value], axis=0)

    def set_by_name(self, k, v):
        self.__setattr__(k, v)

    def process(self, names: str | list, fn: Callable):
        if isinstance(names, str):
            self.__dict__[names] = np.array(fn(self.__dict__[names]))
        else:
            for name in names:
                self.__dict__[name] = np.array(fn(self.__dict__[name]))

    def overwrite(self, k, v):
        self.__dict__[k] = np.array(v)


class DictToClass(BaseGet):
    
    def __init__(self, d: dict) -> None:
        super().__init__()
        
        for k, v in d.items():
            setattr(self, k, v)

    def __setattr__(self, __name: str, __value: Any) -> None:
        self.__dict__[__name] = __value

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def save(self):
        
        save_pk(self.get_dict(), self.path.with_suffix('.pk'))
        save_dict_as_yaml(self.get_dict(), self.path.with_suffix('.yaml'))

    def merge(self, 
              d_new: dict, 
              tag: str | None = None, 
              overwrite: bool = False, 
              only_matching: bool = False):
        
        if not overwrite:
            print(f'Not updating {[k for k in d_new.keys() if k not in self.keys()]}')
            d_new_filtered = {k:v for k,v in d_new.items() if k not in self.keys()}
        
        if only_matching:
            d_new_filtered = {k:v for k,v in d_new_filtered.items() if k in self.keys()}
        
        for k, v in d_new_filtered.items():
            setattr(self, k, v)
        
        if not tag is None:
            setattr(self, tag, d_new)


# class Cfg(DictToClass):
    
#     def __init__(self, d: dict) -> None:
#         super().__init__(d = d)

#         self.path = Path(*(self.run_dir, 'cfg.pk'))
#         self.state_file = join_and_mkdir(self.run_dir, 'state', 'i{:d}.pk')

#         pretty_print_dict(self.get_dict(), header='Config')

#         self.save()

#     def update_cfg_files(self):
        
#         cfg_old = load_pk(self.path)
        
#         for (k, v), v_old in zip(self.items(), cfg_old.values()):
#             if k in cfg_old.keys():
#                 if not v_old == v:
#                     print(f'Updating an original cfg parameter {k} from {v_old} to {v}')
#             else:
#                 print(f'Adding new key: ', k)
    
#         self.save()


# def generate_cfg(path: str) -> Cfg:
#     command_line_args = collect_args()
#     cfg = load_yaml(path) 
#     cfg = cfg | {k:type(cfg[k])(v) for k, v in command_line_args.items()}
#     cfg = Cfg(cfg)
#     return cfg
