from typing import Any, Callable, Iterable, TextIO
from pathlib import Path
from time import time
from datetime import datetime
from zipfile import ZipFile

import numpy as np
import pandas as pd
import string
import random
import json
import pickle as pk

from difflib import get_close_matches

''' NOTES
Details on distinguishing between dicts / classes etc
https://towardsdatascience.com/battle-of-the-data-containers-which-python-typed-structure-is-the-best-6d28fde824e

JSON Allowed types: Dictionary List Tuple String Integer Float Boolean None
'''

TODAY = datetime.today()
ascii_uppercase = string.ascii_uppercase
ascii_lowercase = string.ascii_lowercase

### HANDLING DIRECTORIES & PATHS ###
def mkdir(path: str | Path):
    path = Path(path)
    if path.suffix != '':
        path = path.parent
    if path.exists():
        print('path exists, leaving alone')
    else:
        path.mkdir(parents=True)
    return path


### HANDLING FILES ###
def find_file(path, name):
    f = list(path.rglob(name))
    if len(f) > 1:
        print('More than one file found, use find files to get all')
    return f[0]

def write_dict_to_json(d: dict, f: TextIO):
    # TODO
    return 

def save_pk(x: Any, path: str | Path):
    with open(path, 'wb') as f:
        pk.dump(x, f)
    return

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
def zip_files(path: Path | list[Path], zip_root: Path, name='files.zip'):
    
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
def gen_alphanum(n=7):
    numbers = ''.join([str(i) for i in range(10)])
    characters = ascii_uppercase + ascii_lowercase + numbers
    name = ''.join([random.choice(characters) for _ in range(n)])
    return name

def gen_datetime() -> str:
    return datetime.now().strftime("%d%b%H%M%S")

def now_tag() -> str:
    return datetime.now().strftime('%M%S')

def date_to_num():
    tdelta = TODAY - datetime(year=TODAY.year, month=1, day=1) 
    name = f'{str(TODAY.year)[2:]}_{tdelta.days}_{str(tdelta.microseconds)[-4:]}'
    return name

def add_to_Path(path: Path, string: str | Path):
        return Path(str(path) + str(string))

def iterate_folder(folder: Path):
    exist = [int(x.name.split('-')[1]) for x in folder.iterdir() if '-' in x.name]
    for i in range(100):
        if not i in exist:
            return add_to_Path(folder, f'-{i}')
    raise Exception


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
    
    def __init__(self, d: dict) -> None:
        super().__init__()

        for k, v in d.items():
            setattr(self, k, v)

    def __setattr__(self, k: str, v: Any) -> None:
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


### BETA ### 
def gen_similar(k: str):
    k_s = k + 's' if not k[-1] == 's' else k[:-1]
    return [k, k_s]

dictionary = {
    'd': ['dict', 'dic', 'd'],
    'keys': ['key', 'k', 'ky'],
}


def remove_files_dep():
    from pathlib import Path
    from shutil import copytree, copyfile, rmtree
    import shutil

    root = Path('/home/energy/amawi/projects/nn_ansatz/src/experiments/HEG/final1001/14el/baseline/kfac_1lr-3_1d-4_1nc-4_m2048_el14_s128_p32_l3_det1')
    target = Path('/home/energy/amawi/projects/nn_ansatz/src/experiments/PRX_Responses/runs')
    cfg_paths = root.rglob('config*')

    for p in cfg_paths:
        target_dir = (target / p.relative_to(root)).parent

        if not target_dir.exists():
            target_dir.mkdir(parents=True)

        cfg = target_dir / p.name
        if cfg.exists():
            try:
                cfg.unlink()
            except:
                rmtree(cfg)

        copyfile(p, cfg)
        copytree(str(p.parent / 'models'), str(target_dir / 'models'), dirs_exist_ok=True, )



def mkdir_dep(path: Path, generative: bool = False, exist_ok: bool = False, fail_if_exist: bool = False) -> Path:
    ''' TOOL FOR MAKING DIRECTORIES AND CHANGING THE NAME IF IT ALREADY EXISTS '''
    path = Path(path)
    
    if path.suffix != '':
        folder = path.parent
        name = path.name
    else:
        folder = path
        name = ''


    if generative:
        if folder.exists():
            date_tag = date_to_num()
            folder = add_to_Path(folder, date_tag)

    if exist_ok:
        folder.mkdir(parents=True, exist_ok=exist_ok)
    else:
        if folder.exists():
            if fail_if_exist:
                folder.mkdir(parents=True)  # else does nothing and leaves 
        else:
            folder.mkdir(parents=True)
    
    path = folder / name
    return path


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