
# from typing import Callable
# int, float, str, dict, list, tuple since python 3.10+ 

import sys
from importlib import import_module

from typing import Any, Callable, Iterable, TextIO
from ast import literal_eval
from pathlib import Path
import pprint

from walle.idiomatic import zip_in_n_chunks
from walle.bureaucrat import gen_alphanum, count_device, Config

# TODO fix collect args for lists
# TODO export to json
# TODO if the name exists iterate
# TODO exp_name exists handled at top level


def walk_up_to_git_from_here():
    this_dir = Path(__file__)
    for p in Path(this_dir).absolute().parents:
        if (p / '.git').is_file():
            return p 

DATA_DIR = Path('~/data')
PROJECT_DIR = walk_up_to_git_from_here()
PROJECT_NAME = PROJECT_DIR.name

EXP_ALL_DIR = PROJECT_DIR / 'exp'
CFG_DIR = PROJECT_DIR / 'cfg'

# USER@SERVER AND WANDB ENTITY 
SERVER      = 'server_id'
USER        = 'user_id'
ENTITY      = "xmax1"  


def get_config(exp_path: str = None) -> Config:
    if exp_path is None:
        ''' generates config for  
    
        NB '''

        job_type:       str     = 'training'
        project_name:   str     = PROJECT_NAME   # wandb cfg
        entity:         str     = ENTITY
        n_device:       int     = count_device()
        dtype:          str     = 'f32'

        exp_name:       str     = 'junk'
        exp_id:         str     = gen_alphanum(n=7)
        exp_path:       Path    = EXP_ALL_DIR / exp_name / exp_id

        n_epoch:        int     = 100
        b_size:         int     = 32
        lr:             float   = 0.001

        n_layer:        int     = 3
        af:             str     = 'tanh'    # activation function

        log_metric_it:  int     = 100
        log_state_it:   int     = 1000

        c = locals()
        cmd_line_arg = collect_sysarg()
        cmd_line_arg_typed = create_typed(cmd_line_arg)
        c |= cmd_line_arg_typed  # TODO: check works in place. | is the union two dicts
        c = Config(c)
    
    else:  
        ''' generates config for  
    
        NB '''

        c = import_module((exp_path := Path(exp_path / 'config.py'))).get_config()
        c.exp_path = exp_path
        c.exp_name = exp_path.parent.name
        c.exp_id = exp_path.name
    return c

    


booleans = ['True', 'true', 't', 'False', 'false', 'f']

def create_typed(arg: dict) -> dict:
    """ converts command line arguments to types
    NB  works with [bytes, numbers, tuples, lists, dicts, sets, booleans, None, Ellipsis]
    NB  crashes on string, so an exception is called (TODO: why)
    """
    arg_typed = {}
    for k, v in arg.items():
        
        if v in booleans:                           # REDUNDANCY: The boolean argument isn't written correct
            arg_typed[k] = ('t' in v) or ('T' in v)
        
        else:
            try:
                arg_typed[k] = literal_eval(v)
            except Exception as e:
                arg_typed[k] = str(v)

    return arg_typed


def collect_sysarg() -> dict:
    """
    NB  assumes arguments to any experiment are --arg_name value
    EDU .replace default is replace all arg0 with arg1
    """ 
    if len(sys.argv) == 1:
        return {}
    else:
        
        arg = [a.replace('-', '').replace(' ', '') for a in sys.argv[1:]]  
        
        return {k:v for k,v in zip_in_n_chunks(arg, 2)}


if __name__ == '__main__':

    # python config.py --wstring string --wfloat 0.1 --wint 1 --wbool true --wlist [1,2,3]  # list constrained to no spaces
    args = collect_sysarg()
    args = create_typed(args)

    for k, v in args.items():
        print(k, v, type(v))


    '''
- project
    - exp
        - exp_name0
            - exp_id0
                - res_id0.json
                - cfg_id0.py
            - exp_id1
            - ...
            - res 
            - code (project code for this exp_name run)
            - analysis.ipynb 
            - cfg.py
        - exp_name1
        - ...
        - analysis_template.ipynb (copied into exp_name when exp_name run)
    - cfg
        - cfg.py (copied into exp_name when exp_name run)
    - data
    - project
        - notes
        - walle_src (all walle source)
        - wmodel
            - torch_diff.py
            - jax_mnist.py
            - ...
        - algs.py (function based version of run.py)
        - slurm.py (not used via walle core because likely user submission highly custom)

    - user.py (comes blank, contains credentials, is gitignored)
    - .gitignore (github python boilerplate + extras)

'''