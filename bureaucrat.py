from typing import Any, Callable, Iterable, TextIO, Tuple
from subprocess import check_output
from pathlib import Path
import string
import random
from datetime import datetime
from time import time
from zipfile import ZipFile
from inspect import signature, Parameter

import yaml 
import pickle as pk
import numpy as np
import pandas as pd


# UTILITY WRAPPERS

def robust_wrapper(fn):
    """ Wrapper for non-essential fns, allowing code to run in the face of bugs
    
    - @robust_wrapper(arg0=val, ..., ) potential in idea zone
    - otherwise uses defaults (predefined)

    NB// 
    discussion on nested wrappers 
    https://stackoverflow.com/questions/30904486/python-wrapper-function-taking-arguments-inside-decorator
    """
    
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


@robust_wrapper
def track_time(
    step: int, 
    total_step: int, 
    t0: float, 
    every_n: int=10,
    tag: str=''
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



# GIT

def commit(exp_name: str) -> str:
    ''' 
    
    NB
    - Don't need to include walle functionality because assuming walle stable
    '''

    import os

    cwd = os.getcwd()
    os.chdir(PROJECT_HEAD)  # make sure we are calling git from the right place
    os.system('git add .')
    os.system(f'git commit -m {exp_name}')
    log = check_output('git log').decode('utf-8')  
    commitid = log.replace('\n', ' ').split(' ')[1]
    os.chdir(cwd)
    return commitid


# HANDLING FILES & DIRECTORIES & PATHS
''' NOTES
PATHLIB
make directory parent.mkdir(parents=True, exist_ok=False)
name takes the directory name if called on directory
x / '' = x
'''
def add_to_Path(path: Path, string: str | Path):
    return Path(str(path) + str(string))


def mkdir(path: Path, generative: bool = False, exist_ok: bool = False, fail_if_exist: bool = False) -> Path:
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


def reorder_and_filter_paths(run_root: Path):
    root_all = [str(x) for x in run_root.iterdir() if 'run' in str(root.name)]

    rs_all = np.zeros(len(root_all))
    for i, root in enumerate(root_all):
        cfg = load_pk(root / 'config1.pk')
        rs_all[i] = [cfg['density_parameter']]
    order = np.argsort(rs_all)
    
    return [Path(root_all[i]) for i in order]


# TIMING

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


def auto_type():

    def typed_fn():

        return 

    return 


def join_and_mkdir(*args):
    """
    takes a path
    removes the filename if filepath 
    creates the directory if it doesn't exist 
    returns the whole path 
    
    NB//
    star operator turns it into a tuple even if single element, 
    therefore this works for just making dirs
    """
    path = Path(*args)
    mkdir(path)
    return path


def find_file(path, name):
    f = list(path.rglob(name))
    if len(f) > 1:
        print('More than one file found, use find files to get all')
    return f[0]


# YAML

class Array(yaml.YAMLObject):
    '''
    definition of a yaml descriptor
    node: all the characters indented after the name
    decomposes to a sequence and can iterate over the sequence by its value
    
    from yaml import ScalarNode
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

        return np.array(array)


def load_yaml(path: str) -> dict:
    with open(path, 'r') as f:
        args = yaml.load(f, Loader=yaml.FullLoader)
    return args


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
    """ like this to allow recursion """
    with open(path, 'w') as f:
        write_dict(d, f)


# numpy 

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


# pickle

def save_pk(x: Any, path: Path):
    
    if isinstance(x, dict):
        x = {k: to_numpy(v) for k, v in x.items()}
    else:
        x = to_numpy(x)

    with open(path, 'wb') as f:
        pk.dump(x, f)


def load_pk(path: str) -> dict | np.ndarray:
    with open(path, 'rb') as f:
        x = pk.load(f)
    return x


def check_content_pk(d: dict | np.ndarray):
    for k, v in d.items():
        print(k, v.shape)


# pandas

def df_to_dict(df: pd.DataFrame, type_filter: list = []) -> dict:
    return {c:np.array(df[c]) for c in df.columns if df[c].dtypes not in type_filter}


# create zip file


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


# NAMING

def gen_alphanum(n=10):
    uppers = string.ascii_uppercase
    lowers = string.ascii_lowercase
    numbers = ''.join([str(i) for i in range(10)])
    characters = uppers + lowers + numbers
    name = ''.join([random.choice(characters) for i in range(n)]) + '.pk'
    return name

def gen_datetime() -> str:
    return datetime.now().strftime("%d%b%H%M%S")

def now_tag() -> str:
    return datetime.now().strftime('%M%S')

def date_to_num():
    today = datetime.today()
    tdelta = today - datetime(year=today.year, month=1, day=1) 
    name = f'{str(today.year)[2:]}_{tdelta.days}_{str(tdelta.microseconds)[-4:]}'
    return name

def iterate_folder(folder: Path):
    exist = [int(x.split('-')[1]) for x in folder.iterdir() if '-' in x.name]
    for i in range(100):
        if i in exist:
            break
    folder = add_to_Path(folder, f'-{i}')
    return folder

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