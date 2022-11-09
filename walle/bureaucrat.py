from typing import Any, Callable, Iterable, TextIO
from pathlib import Path
from time import time
from datetime import datetime
from zipfile import ZipFile
from pathlib import Path
from shutil import copytree, copyfile, rmtree

import numpy as np
import pandas as pd
import string
import random
import json
import pickle as pk

from difflib import get_close_matches
from safe_utils import wtype

ascii_uppercase = string.ascii_uppercase
ascii_lowercase = string.ascii_lowercase
sPath = str | Path

''' NOTES
Details on distinguishing between dicts / classes etc
https://towardsdatascience.com/battle-of-the-data-containers-which-python-typed-structure-is-the-best-6d28fde824e

JSON Allowed types: Dictionary List Tuple String Integer Float Boolean None
'''

def gen_datetime() -> str:
    return datetime.now().strftime("%d%b%H%M%S")

def now_tag() -> str:
    return datetime.now().strftime('%M%S')

def date_to_num():
    tdelta = today - datetime(year=today.year, month=1, day=1) 
    name = f'{str(today.year)[2:]}_{tdelta.days}_{str(tdelta.microseconds)[-4:]}'
    return name

today = datetime.today()
today_n = date_to_num()

### HANDLING DIRECTORIES & PATHS ###
@wtype
def mkdir(path: Path) -> Path:
    if path.suffix != '':
        path = path.parent
    if path.exists():
        print('path exists, leaving alone')
    else:
        path.mkdir(parents=True)
    return path

### HANDLING FILES ###
def find_file(path: Path, name: str) -> Path:
    f = list(path.rglob(name))
    if len(f) > 1:
        print('More than one file found, use find files to get all')
    return f[0]

def write_dict_to_json(d: dict, f: TextIO):
    # TODO
    return 

def save_pk(x: Any, path: Path):
    with open(path, 'wb') as f:
        pk.dump(x, f)

def load_pk(path: str | Path):
    with open(path, 'rb') as f:
        x = pk.load(f)
    return x

def load_json(path: str | Path) -> dict:
    with open(path, 'r') as f:
        x = json.load(f, indent=4, separators=(',', ':'))
    return x

def save_json(x: Any, path: str | Path):
    with open(path, 'w') as f:
        json.dump(x, f, indent=4, separators=(',', ':'))
    return

def check_content_dict(d: dict | np.ndarray):
    for k, v in d.items():
        print(k, v.shape)

### TYPES ####
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

### PANDAS ###
def df_to_dict(df: pd.DataFrame, type_filter: list = []) -> dict:
    return {c:np.array(df[c]) for c in df.columns if df[c].dtypes not in type_filter}


### ZIP ###
def zip_files(path: Path | list[Path], zip_root: Path, name: str = 'files.zip'):
    
    if isinstance(path, list):
        pass
    elif path.is_dir():
        path = path.iterdir()
    elif path.is_file():
        path = [path]
    
    print(f'Zipping {len(list(path))} files in {name}')
    with ZipFile(name, 'w') as f:
        for p in path:
            arcname = p.relative_to(zip_root)          
            f.write(str(p), arcname=arcname)


### NAMING ###
def gen_alphanum(n: int = 7):
    numbers = ''.join([str(i) for i in range(10)])
    characters = ascii_uppercase + ascii_lowercase + numbers
    name = ''.join([random.choice(characters) for _ in range(n)])
    return name

def add_to_Path(path: Path, string: str | Path):
        return Path(str(path) + str(string))

def iterate_folder(folder: Path):
    exist = [int(x.name.split('-')[1]) for x in folder.iterdir() if '-' in x.name]
    for i in range(100):
        if not i in exist:
            return add_to_Path(folder, f'-{i}')
    raise Exception

@wtype
def remove_path(path: Path):
    if path.exists():
        if path.is_file():
            path.unlink()
        else:
            rmtree(path)

### TESTING ###
def tests():
    from .idiomatic import flatten_lst_of_lst
    path = Path(r'C:\Users\max\OneDrive\sisy\hwapnet\analysis\PRX_responses\runs')
    match =  ['exp_stats_pair_corr_d3_new', 'exp_stats_one_body_d3', 'exp_stats_mom_dist_3', 'config.pk']
    files = [path.rglob(f'*{m}*') for m in match]
    files = flatten_lst_of_lst(files)
    zip_files(files, name=r'.\runs\results\d3_obs_data.zip', zip_root=path)

    return 


if __name__ == '__main__':

    tests()