import os
from tempfile import TemporaryFile
from typing import Iterable, Union, TextIO, Any
from datetime import datetime
import yaml 
import pickle as pk
import pandas as pd
import numpy as np
from pathlib import Path
try:
    import jax.numpy as jnp
except:
    import numpy as jnp

from prettytable import PrettyTable

PROJECT_HEAD = Path(__file__).parent
assert PROJECT_HEAD.stem == 'walle', f'{PROJECT_HEAD.stem} change project head in boring utils so it points to walle dir plz'


# create exp_name from sweep features


def append_idx(root: str, idx: int = 1) -> str:
    root_tmp = root + f'_{idx}'
    while os.path.exists(root_tmp):
        root_tmp = root + f'_{idx}'
        idx += 1
    return root_tmp


def gen_datetime() -> str:
    return datetime.now().strftime("%d%b%H%M%S")


def now_tag() -> str:
    return datetime.now().strftime('%M%S')


def format_value(value: float | str | int | list) -> str:
    
    if isinstance(value, float): # takes 2 significant figures automatically
        return f'{value:.2g}'  
    
    elif isinstance(value, str):
        return value[:5].capitalize()
    
    elif isinstance(value, int): # limit length of ints to 4
        return str(value)[:4]
    
    elif isinstance(value, list):
        value = next((x for x in value if x), 0.0)
        return f'{value:.2g}' 
    
    else:
        raise Exception(f'Input cfg {value} not accepted type')


def create_sweep_exp_filename(sweep_cfg: dict) -> str:
    
    sweep_cfg = {k:sweep_cfg[k] for k in sorted(sweep_cfg.keys())}
    
    name = []
    for k, v in sweep_cfg.items():
        k = k.split('_')
        name += ''.join([s[0] for s in k])
        name += format_value(v)
    name = '_'.join(name)
    
    return name


# conversions


def df_to_dict(df: pd.DataFrame, type_filter: list = []) -> dict:
    return {c:np.array(df[c]) for c in df.columns if df[c].dtypes not in type_filter}


# printing 


def pretty_print_dict(d: dict, header: str | None = None):
    
    if not header is None:
        print(header)
    
    # print_tmp = print(f'{k}: {(' ' * whitespace):str} {v} ({type(v).__name__})')
    def print_tmp(k, whitespace, v):
        whitespace = f' ' * whitespace
        print(f'{k}: {whitespace} {v} ({type(v).__name__})')
    
    max_chars = max([len(k) for k in d.keys()]) + 3
    
    for k, v in d.items():
        v = array_to_lists(v) 
        
        whitespace = max_chars - len(k)  # set the whitespace so all prints are aligned
        
        if isinstance(v, list):
            if isinstance(v[0], list) and len(v) > 1:
                print_tmp(k, whitespace, v[0])
                whitespace += len(k)
                for l in v[1:]:
                    print_tmp('', whitespace, l)
            else:
                print_tmp(k, whitespace, v)
        else:
            print_tmp(k, whitespace, v)


def save_pretty_table(data: dict | pd.DataFrame, 
                      path: str = 'table.txt',
                      top: float = 100.0, 
                      bottom: float = 0.01):

    if isinstance(data, pd.DataFrame):
        data = df_to_dict(data, type_filter=[str, object])
    
    map_small = lambda x: '{:.3f}'.format(x)
    map_big = lambda x: '{:.3e}'.format(x)

    table = PrettyTable()
    for k, v in data.items():
        v = np.squeeze(v)
        if v.ndim == 1:
            
            v = map(map_small, v) if ((top > v).all() and (v > bottom).all()) else map(map_big, v)
            
            table.add_column(k, list(v))

    with open(path, 'w') as f:
        f.write(str(table))


# handling files

oj = Path

def ojm(*args):
    '''
    star operator here turns it into a tuple even if single element, 
    therefore this works for just making dirs
    
    takes a path
    removes the filename if filepath 
    creates the directory if it doesn't exist 
    returns the whole path 
    '''
    path = Path(*args)
    if path.suffix != '':
        root = path.parent
    else:
        root = path
    root.mkdir(parents=True, exist_ok=True)
    return path


def save_pk(data: dict | np.ndarray, path: str):
    with open(path, 'wb') as f:
        pk.dump(data, f)


def load_pk(path: str) -> dict | np.ndarray:
    with open(path, 'rb') as f:
        x = pk.load(f)
    return x


try:
    from jax.numpy import array as make_array
except:
    from numpy import array as make_array

from yaml import ScalarNode

class Array(yaml.YAMLObject):
    '''
    definition of a yaml descriptor
    node: all the characters indented after the name
    decomposes to a sequence and can iterate over the sequence by its value
    '''
    yaml_tag = u'!jax_or_numpy_arr'
    
    @classmethod
    def from_yaml(cls, constructor, node):
        
        array = []
        for sub_node in node.value:
            print(sub_node.tag)
            if 'seq' in sub_node.tag:
                array.append([float(v.value) if 'float' in v.tag else int(v.value) for v in sub_node.value])
            else:
                array.append(float(sub_node.value) if 'float' in sub_node.tag else int(sub_node.value))

        return make_array(array)


def load_yaml(path: str) -> dict:
    with open(path, 'r') as f:
        args = yaml.load(f, Loader=yaml.FullLoader)
    return args


def array_to_lists(v: Any) -> Any:
    if isinstance(v, np.ndarray) or isinstance(v, jnp.ndarray):
        v = np.array(v)
        if np.isscalar(v):
            v = float(v)
        elif v.ndim == 1:
            v = list(v)
        elif v.ndim == 2:
            v = [list(x) for x in v]
        else:
            print('Can\'t save array with ndim > 2')
    return v


def write_dict(d: dict, f: TextIO):
    for k, v in d.items():
        v = array_to_lists(v)

        if type(v) in [str, int, float]:
            f.writelines(f'{k}: !!{type(v).__name__} {v} \n')
        
        if isinstance(v, list):
            f.writelines('{}: !!seq {} \n'.format(k, v if not isinstance(v[0], list) else ''))
            if isinstance(v[0], list):
                for l in v: 
                    f.writelines(f'  - !!seq {l} \n')

        if isinstance(v, dict):
            f.writelines(f'{k}: !!map \n')
            write_dict(v, f)

        if isinstance(v, Path):
            f.writelines(f'{k}: !!str {v.as_posix()} \n')
    return 


def save_dict_as_yaml(d: dict, path: str):
    ''' like this to allow recursion '''
    with open(path, 'w') as f:
        write_dict(d, f)
        

                
                

                



# The Bone Zone 

def save_pretty_table_pandas(df: pd.DataFrame, path='table.txt', cols=None, top=100, bottom=0.01):
    
    if cols is None: cols = df.columns

    table = PrettyTable()
    for c in cols:
        if df[c].dtypes not in [str, object]:
            if (top > df[c]).all() and (df[c] > bottom).all():
                df[c] = df[c].map(lambda x: '{:.3f}'.format(x))
            else:
                df[c] = df[c].map(lambda x: '{:.3e}'.format(x))
            
            table.add_column(c, list(df[c]))

    with open(path, 'w') as f:
        f.write(str(table))