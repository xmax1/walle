import sys
import os
from typing import Callable, Any
from inspect import signature
from subprocess import check_output
from dataclasses import dataclass, fields
from ast import literal_eval
from pathlib import Path

import yaml 
import pickle as pk
import pandas as pd
import numpy as np

from boring_utils import *
from idioms import *

THIS_DIR = Path(__file__).parent


# experiment management


def commit(exp_name: str) -> str:
    cwd = os.getcwd()
    os.chdir(PROJECT_HEAD)  # make sure we are calling git from the right place
    os.system('git add .')
    os.system(f'git commit -m {exp_name}')
    log = check_output('git log').decode('utf-8')  
    commitid = log.replace('\n', ' ').split(' ')[1]
    os.chdir(cwd)
    return commitid


def collect_data_dict(d: dict, d_new: dict, process: dict[Callable] = {}):
    '''
    creates or appends (axis=0) new data in a dict to a dict containing previous info
    needs arrays to be squeezed before
    '''
    
    for k, v in d_new.items():
        v = np.array(v)
            
        v = process.get(k, lambda v: v)(v)  # applies a function to v, if function doesn't exist does nothing
    
        if k not in d.keys():
            if isinstance(v, np.ndarray): d[k] = v
            else: d[k] = [v]
        else:
            if isinstance(v, np.ndarray): d[k] = np.concatenate([d[k], v])
            else: d[k].append(v)
    
    return d


# Configuration utils 

booleans = ['True', 'true', 't', 'False', 'false', 'f']


def create_types(args: dict) -> dict:
    '''
    converts command line arguments to types
    works with [bytes, numbers, tuples, lists, dicts, sets, booleans, None, Ellipsis]
    crashes on string, so an exception is called
    '''

    typed_args = {}
    for k, v in args.items():
        
        if v in booleans:  # in case the boolean argument isn't written correct
            v = ('t' in v) or ('T' in v)
        else:
            try:
                v = literal_eval(v)
            except Exception as e:
                v = str(v)

        typed_args[k] = v
    
    return typed_args


def collect_args() -> dict:
    # assumes arguments to any experiment are --arg_name value
    
    if len(sys.argv) == 1:
        args = {}
    else:
        args = iter(sys.argv[1:])
        args = ' '.join(sys.argv[1:])
        args = args.split('--')[1:]  # first element is blank, 
        args = [a.split(' ', 1) for a in args]  # split(chat, max_splits) 
        args = [x.replace(' ', '') for sub_list in args for x in sub_list]  # make iterable so can iterate in 2s
        args = {k.replace('-', ''):v for k, v in zip_in_n_chunks(args, 2)}

        # alternate
        args = iter(sys.argv[1:])
        args = [a.replace('-', '').replace(' ', '') for a in args]  # replace default is to replace all values
        args = {k:v for k, v in zip_in_n_chunks(args, 2)}
    
    return args


class DictToClass():
    def __init__(self, d: dict) -> None:
        print('here')
        for k, v in d.items():
            setattr(self, k, v)

    def get(self, name: str, alternate: str | None = None) -> Any:
        return self.get_dict().get(name, alternate)

    def __setattr__(self, __name: str, __value: Any) -> None:
        self.__dict__[__name] = __value

    def get_dict(self):
        return self.__dict__

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def get(self, name: str, alternate: str | None = None) -> Any:
        return self.get_dict().get(name, alternate)

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


def save_dict_as_pk_and_yaml(d: dict, path: Path):
    save_pk(d, path.with_suffix('.pk'))
    save_dict_as_yaml(d, path.with_suffix('.yaml'))


class Cfg(DictToClass):
    
    def __init__(self, d: dict) -> None:
        super().__init__(d = d)

        self.path = Path(*(self.run_dir, 'cfg.pk'))
        self.state_file = ojm(self.run_dir, 'state', 'i{:d}.pk')

        pretty_print_dict(self.get_dict(), header='Config')

        self.save()

    def update_cfg_files(self):
        
        cfg_old = load_pk(self.path)
        
        for (k, v), v_old in zip(self.items(), cfg_old.values()):
            if k in cfg_old.keys():
                if not v_old == v:
                    print(f'Updating an original cfg parameter {k} from {v_old} to {v}')
            else:
                print(f'Adding new key: ', k)
    
        self.save()

    


        
    
def generate_cfg(path: str) -> Cfg:
    command_line_args = collect_args()
    cfg = load_yaml(path) 
    cfg = cfg | {k:type(cfg[k])(v) for k, v in command_line_args.items()}
    cfg = Cfg(cfg)
    return cfg


### The Bone Zone


def generate_cfg_from_dataclass(args: dict, cfg: dataclass) -> dataclass:
    '''
    what does f.init do? 
    '''
    
    fields = {f.name for f in fields(cfg) if f.init}
    assert args.keys().issubset(field_set)
    field_types = cfg.__annotations__  # returns dictionary of {attribute: type}
    
    typed_args = {}
    for k, v in args.items():
        typed_args[k] = field_types[k](v)

    pretty_print_dict(typed_args)

    return cfg(**typed_args)


if __name__ == '__main__':

    x = {'t':1, 'a':'max'}
    x = ClassFromDict(x)

    def fn(t=10, a='z'):
        print(t, a)

    fn(**x)










'''
    

def append_to_txt(path, data):
    with open(path, 'a') as f:
        f.write('\n ' + data)


def append_dict_to_dict(d, d_new):
    for k, v in d_new.items():
        if k not in d.keys():
            if isinstance(v, np.ndarray):
                d[k] = v
            else:
                d[k] = [v]
        else:
            if isinstance(v, np.ndarray):
                d[k] = np.concatenate([d[k], v])
            else:
                d[k].append(v)
    return d



def load_pk(path):
    with open(path, 'rb') as f:
        x = pk.load(f)
    return x 


def load_yaml(path):
    with open(path) as f:
        sweep_cfg = yaml.safe_load(f)
    return sweep_cfg


def save_pk_and_csv(x, path):
    with open(path+'.pk', 'wb') as f:
        pk.dump(x, f)
    x = {k: ([v] if not isinstance(v, list) else v) for k, v in x.items()}  # needs at least one and values in lists
    df = pd.DataFrame.from_dict(x) 
    df.to_csv (path+'.csv', index = False, header=True)


def mkdirs(path):
    if not os.path.exists(path): os.makedirs(path)


def make_arg_key(key):
    key = key.replace('-', '')
    return key





annotation_eval = [str,]


def type_args(args, fn):
    sig_params = signature(fn).parameters
    typed_args = {}
    for k, v in args.items():
        try:
            v = literal_eval(v)
        except Exception as e:
            print(v, str(v), e)
            v = str(v)

        # arg_type = sig_params[k].annotation
        # if arg_type in annotation_eval:
        #     v = arg_type(v)
        # else:
        #     v = literal_eval(v)

        typed_args[k] = v
    for k, v in typed_args.items():
        print(k, v, type(v))
    return typed_args




def run_fn_with_sysargs(fn):
    args = collect_args()
    typed_args = type_args(args, fn)
    fn(**typed_args)




'''
