from typing import Any, Iterable, TextIO
from pathlib import Path
from datetime import datetime
from shutil import rmtree

import numpy as np
import pandas as pd
import string
import random
import json
import re

ascii_uppercase = string.ascii_uppercase
ascii_lowercase = string.ascii_lowercase
sPath = str | Path

''' NOTES
Details on distinguishing between dicts / classes etc
https://towardsdatascience.com/battle-of-the-data-containers-which-python-typed-structure-is-the-best-6d28fde824e

JSON Allowed types: dict list tuple str int float bool None
'''

today = datetime.today()

JSON_INDENT = 4
JSON_SEP = (',', ':')

def gen_datetime() -> str:
    return datetime.now().strftime("%d%b%H%M%S")

def now_tag() -> str:
    return datetime.now().strftime('%M%S')

def date_to_num():
    tdelta = today - datetime(year=today.year, month=1, day=1) 
    name = f'{str(today.year)[2:]}_{tdelta.days}_{str(tdelta.microseconds)[-4:]}'
    return name

today_n = date_to_num()

### HANDLING DIRECTORIES & PATHS ###
def mkdir(path: Path) -> Path:
    path = Path(path)
    if path.suffix != '':
        path = path.parent
    if path.exists():
        print('path exists, leaving alone')
    else:
        path.mkdir(parents=True)
    return path

### HANDLING FILES ###
def load_json(path: str | Path) -> dict:
    """ load a dict as json file at path converting all iterables to numpy arrays """
    with open(path, 'r') as f:
        d = json.load(f, indent=JSON_INDENT, separators=JSON_SEP)
    if isinstance(d, dict):
        d = {k:np.array(v) if isinstance(v, list|tuple) else v for k,v in d.items()}
    elif isinstance(d, list|tuple):
        d = np.array(d)
    return d

def save_json(d: dict, path: Path):
    """ save a dict as json file at path """
    for k, v in d.items():
        if is_array(v):
            d[k] = np.array(v).tolist()
        if isinstance(v, Path):
            d[k] = str(v)
    with open(path, 'w') as f:
        json.dump(d, f, indent=JSON_INDENT, separators=JSON_SEP)

def find_file(path: Path, name: str) -> Path:
    f = list(path.rglob(name))
    if len(f) > 1:
        print('More than one file found, use find files to get all')
    return f[0]

def check_content_dict(d: dict | np.ndarray):
    for k, v in d.items():
        print(k, v.shape)

### TYPES ####
def is_array(x: Any):
    return ('shape' in dir(x))

def to_numpy(x: Any):
    """ converts arrays and lists to numpy, else does nothing """
    if isinstance(x, Iterable):
        return np.array(x)
    elif isinstance(x, (float, int, str, Path)):
        return x
    else:
        print(f'to_numpy does not recognise {type(x)}')
        
def array_to_lists(v: np.ndarray | float | int) -> Any:
    if np.isscalar(v):
        v = float(v)
    if isinstance(v, np.ndarray):
        if v.ndim == 1:
            v = list(v)
        elif v.ndim == 2:
            v = [list(x) for x in v]
        else:
            print('Can\'t save array with ndim > 2')
    return v

def to_standard_type(x: Any):
    if isinstance(x, Iterable):
        return np.array(x)
    elif isinstance(x, Path):
        return x
    elif isinstance(x, float | int | str):
        return x
    else:
        print(f'to_standard_type does not recognise {type(x)}')

### NAMING ###
def gen_alphanum(n: int = 7, test=False):
    random.seed(test if test else None)
    numbers = ''.join([str(i) for i in range(10)])
    characters = ascii_uppercase + ascii_lowercase + numbers
    name = ''.join([random.choice(characters) for _ in range(n)])
    return name

def add_to_Path(path: Path, string: str | Path):
        return Path(str(path) + str(string))

def iterate_folder(folder: Path, on=True):
    if not on:
        return folder
    if folder.exists():
        if '-':
            ...
    if re.search(folder.name, {folder.name})
    if re.search(folder.name, f'-[0-9]*'):
        print(f'exp {folder} exists')
        exist = [int(x.name.split('-')[-1]) for x in folder.parent.iterdir() if '-' in x.name]
        for i in range(100):
            if not i in exist:
                folder = add_to_Path(folder, f'-{i}')
    print(f'created exp_dir {folder}')
    return folder

def remove_path(path: Path):
    if path.exists():
        if path.is_file():
            path.unlink()
        else:
            rmtree(path)

### TESTING ###
def tests():
    return 

if __name__ == '__main__':
    tests()