from pathlib import Path
import re
from walle.bureaucrat import iterate_folder, gen_alphanum, mkdir, date_to_num, today
from submit import get_sys_arg
from importlib import import_module

class Pyfig:
    def __init__(self, d: dict) -> None:
        for k,v in d.items():
            setattr(self, k, v)

    @property
    def dict(self):
        return self.__dict__

def pyfig(*, create_exp=True, iterate_exp_name=True, n_clean=20, **kwarg):        
        
        c = Pyfig(import_module(kwarg['cfg_path']).Config)

        if iterate_exp_name:
            exp_all = [p for p in c.project_exp_dir.iterdir() if p.is_dir()]
            n_exp_in_path = len(exp_all)
            if n_exp_in_path > n_clean:
                dump_dir = c.project_exp_dir / (date_to_num()+'_'+today)
                [p.rename(dump_dir / p.name) for p in exp_all]

            c.exp_path = iterate_folder(c.project_exp_dir/c.exp_name)
        
        if not c.sweep: # bool(empty dictionary) = False
            c.exp_path /= gen_alphanum(n=7)

        if create_exp:
            write_pyfig(c)


def write_pyfig(c: Pyfig):

    with open(c.source, 'r') as f:
        l_source = f.readlines()
    
    with open(mkdir(c.exp_path), 'w') as f:
        for l in l_source:
            for name, val in c.dict.items():
                if not '_' == name[0] and re.search(name, l):
                    lhs, rhs = re.search('= *[^(#|\r\n|\r|\n)]*', l).span()
                    l = [l[:lhs], f' {val} ', l[rhs:]]
            f.writelines(l)

class wContext:
    def __init__(self, protect:bool=False):
        self.protect = protect
    def __enter__(self):
        self._var = set(globals())
        return self
    def __exit__(self, *args):
        self.k = [self.protect*'_'+k for k in list(set(globals()) - self._var)]

if __name__ == '__main__':
    cfg_path = r'..\cfg\cfg.py'
    c = pyfig(cfg_path=cfg_path)



# @wtype
# def gen_cfg(cfg_path: Path = None, default_path: Path = '../cfg/cfg.py'):
#     """ sets a cfg_path
#     setdefault returns key if exists else replaces the key """
#     cmd_line_arg = get_sys_arg()
#     path = cmd_line_arg.setdefault('cfg_path', cfg_path if cfg_path is not None else default_path)
#     c = import_module(path).Cfg(cmd_line_arg)
#     c.write()
#     return c

# # @wtype
# def load_cfg(cfg_path: Path = None, default_path: Path = '../cfg/cfg.py'):
#     """ sets a cfg_path
#     setdefault returns key if exists else replaces the key """
#     cmd_line_arg = get_sys_arg()
#     path = cmd_line_arg.setdefault('cfg_path', cfg_path if cfg_path is not None else default_path)
#     return import_module(path).Cfg(cmd_line_arg)

# # @wtype
# def pyfig(cfg_path: Path = None, default_path: Path = '../cfg/cfg.py', setup=True, iterate_exp_name=True):
#     """ sets a cfg_path
#     setdefault returns key if exists else replaces the key """
#     cmd_line_arg = get_sys_arg()
#     path = cmd_line_arg.setdefault('cfg_path', cfg_path if cfg_path is not None else default_path)
#     return import_module(path).Cfg(cmd_line_arg)






# def save_pyfig(source: Path, target: Path, write_d: dict):    
#     n_lines_changed = 0

#     with open(source, 'r') as f:
#         l_source = f.readlines()
    
#     with open(mkdir(target), 'w') as f:
        
#         for l in l_source:
#             if re.search('sweep *= *dict', l):   
#                 while not re.search('END', l):  #  '^\s' matches whitespace at start
#                     f.writelines(l)  
#                     l = next(l_source)
            
#             for name, val in write_d.items():
#                 if re.search(name, l):
#                     lhs, rhs = re.search('= *[^(#|\r\n|\r|\n)]*', l).span()
#                     l = [l[:lhs], f' {val} ', l[rhs:]]
#                     n_lines_changed += 1
        
#             f.writelines(l)
#     assert n_lines_changed == len(write_d)