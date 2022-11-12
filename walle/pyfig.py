from pathlib import Path
import re
from .bureaucrat import iterate_folder, gen_alphanum, mkdir, date_to_num, today
"""
TODO
- regex \\ parsing and replacement                                            
- multiline variables defined by = \\ (single backslash)                                                 
- consistent tab spacing                                                  
- if the variable has changed, update it, raise error if protected 
"""

docs = "                                         \n \
DOCS                                             \n \
                                                 \n \
ALLOWED STRUCTURES                               \n \
- SINGLE LINE STRUCTURES (everything defined on a single line ie n_it: int = 1000)  \n \
    - only variable name and value needed                                           \n \
- MULTILINE STRUCTURES                                                              \n \
    - functions (def \\n)                                                           \n \
    - (BETA) any structure defined by = \\ (single backslash)                       \n \
                                                                                    \n \
DISALLOWED (MUST BE IN PROTECTED CONTEXT)                                           \n \
- ANY MULTILINE STRUCTURE NOT DEFINED BY = \\ (single backslash)                    \n \
"

class ws:
    """ baseline how format pyfig """
    colon       = 15
    var_type    = 30
    eq          = 35
    val         = 40
    comment     = 50

class pattern:
    general_cr  = '\r\n|\r|\n'  # carriage return

def load_pyfig(cfg_path: Path):
    import runpy
    c = runpy.run_path(cfg_path)
    return c.get('Pyfig', c.get(cfg_path.with_suffix('').name))

def pyfig(*, cfg_path=Path('./cfg/cfg.py'), create=True, iterate=True, n_clean=20, test=True, **kwarg):        
    
    c = load_pyfig(cfg_path)
    c |= {'create': create, 'iterate': iterate, **{k:v for k,v in kwarg.items() if k not in c.sys_arg}}

    exp_all = [p for p in c.project_exp_dir.iterdir() if p.is_dir()]
        
    if len(exp_all) > n_clean:
        dump_dir = c.project_exp_dir / (date_to_num()+'_'+today)
        [p.rename(dump_dir / p.name) for p in exp_all]

    if iterate:
        c.exp_path = iterate_folder(c.project_exp_dir/c.exp_name)
    
    if not c.sweep: # bool(empty dictionary) = False
        c.exp_path /= gen_alphanum(n=7, test=test)

    if create:
        mkdir(c.exp_path)
        write_pyfig(c)

def write_pyfig(c: Pyfig, changed: dict):
    
    with open(c.source_path, 'r', encoding='utf-8') as f:
        l_source = f.readlines()
    
    target = (c.exp_path/c.source_path.name)
    target.write_bytes(c.source_path.read_bytes())
    
    i = 0
    with open(target, 'w', encoding='utf-8') as f:     
        while not bool(re.search('globals', l_source[i])):
            i+=1

        while i < len(l_source):
            
            if re.search('protect', l_source[i]):
                while not re.search('^\s', l_source[i]):
                    i += 1

            l = l_source[i]
            for name, val in changed.items():
                if re.search(name, l) and (match := re.search('= *[^#|\r\n|\r|\n]*', l)):
                    lhs, rhs = match.span()
                    lhs = l_source[i][:lhs+1]
                    rhs = l_source[i][rhs:]
                    
                    if isinstance(val, str|Path):
                        val = '\'' + str(val) + '\''

                    l_source[i] = lhs + f' {val} ' + tabs + rhs
                    
                    while not re.search(']', l):
                        i += 1
                        l = l_source[i]
                    break
            i+=1
        
        f.writelines(l_source)
    print(target)



""" CREATE SOME GENERALISED WAY TO EDIT THE DOCUMENT AS IS AND ONLY REPLACE THE VARIABLES
- Broken lists
- \n \ characters
- functions
- only edit sys_arg to make it easier
rhs = re.match(' *\s^', l)[1]
re.sub('\n *\ ', '\\\n \\ ', l, count=1, flags=0)
if (n := len(re.findall(cr, l)-1)):
                    #     re.sub(cr, '\\n', l, count=n, flags=0)
"""


class SubClass:
    def __enter__(self):
        self._var = set(globals())
    def __exit__(self, *args):
        keys = [k for k in list(set(globals()) - self._var)]
        for k in keys:
            setattr(self, k, vars()[k])


if __name__ == '__main__':
    cfg_path = Path(r'C:\Users\max\OneDrive\sisy\walle\cfg\cfg.py')
    mkdir(r'C:\Users\max\OneDrive\sisy\walle\exp')
    print(cfg_path.absolute())
    c = pyfig(cfg_path=Path(cfg_path).absolute())





# >>> from pathlib import Path

# >>> def load_config(config_file):
# ...     config_file = Path(config_file)
# ...     code = compile(config_file.read_text(), config_file.name, "exec")
# ...     config_dict = {}
# ...     exec(code, {"__builtins__": {}}, config_dict)
# ...     return config_dict
# ...

# >>> load_config("settings.conf")
# {
#     'font_face': '',
#     'font_size': 10,
#     'line_numbers': True,
#     'tab_size': 4,
#     'auto_indent': True
# }



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