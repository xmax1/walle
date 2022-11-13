import re
from pathlib import Path
import runpy
from .bureaucrat import iterate_folder, gen_alphanum, mkdir, date_to_num, today

general_cr  = '\r\n|\r|\n'  # carriage return
ws = ' +'
a_string = '^[\"\']\w+[\"\']'
var_pattern = lambda name: f'^{name}[ :]*[a-zA-Z0-9_]* *= *$'

def load_pyfig(cfg_path: Path):
    c = runpy.run_path(cfg_path)
    return c.get('Pyfig', c.get(cfg_path.with_suffix('').name))

def pyfig(*, cfg_path=Path('./cfg/cfg.py'), create=True, iterate=True, n_clean=20, sweep={}, test=True, **kwarg):        
    
    c = load_pyfig(cfg_path)
    c |= {'create': create, 'iterate': iterate, **{k:v for k,v in kwarg.items() if k not in c.sys_arg}}
    
    if sweep:
        c |= sweep

    exp_all = [p for p in c.project_exp_dir.iterdir() if p.is_dir()]
        
    if len(exp_all) > n_clean:
        dump_dir = c.project_exp_dir / (date_to_num()+'_'+today)
        [p.rename(dump_dir / p.name) for p in exp_all]

    if iterate:
        c.exp_path = iterate_folder(c.project_exp_dir/c.exp_name)
    
    if c.run in ['sweep_agent', 'run']: # bool(empty dictionary) = False
        c.exp_path /= gen_alphanum(n=7, test=test)

    if create:
        mkdir(c.exp_path)
        # write_pyfig in beta for writing the file - ditched for wandb configs