

from pathlib import Path
import re
from shutil import copyfile
from typing import Any
from walle.bureaucrat import gen_alphanum, iterate_folder, mkdir
from walle.submit import count_gpu, get_sys_arg, git_commit_id
from walle.wutils import wClass

this_path = Path(__file__)

""" MODES
NB  if user calls remote submission, do we need a flag to understand 
- script 
- sweep
- script server 
- sweep server
- script push to server 
- sweep push to server
"""

""" Cfg journey script
- call Cfg - create exp_path, iterate
"""

""" When do we iterate the exp_name?
- A sweep all needs to be in the same exp_name
- Give the user the option 
"""

""" How to distinguish between a single, a custom, and a wandb? 
- wandb has custom dictionary patterns
- single just wants to iterate every time, or does it?!
"""

""" Cfg journey sweep
- call Cfg - create exp_name path, iterate
    - when the Cfg is called with cmd line args, does the exp_path execute (!!) we want 'no' 
"""

""" How to set when it is being loaded and when it is a normal cfg that needs to write itself? 
"""

"""
exp_name has to be the assigned name
"""

"""
RUN

LOAD
When loaded does nothing but give you the params:
    How to know when loaded? 
"""

""" FEATURES
Assign slurm vars from cmd_line: wclass searches internal dict and replaces

"""

sbatch_cfg  = 'module purge \n \
               source ~/.bashrc \n \
               module load GCC \n \
               module load CUDA/11.4.1 \n \
               module load cuDNN/8.2.2.26-CUDA-11.4.1 \n \
               conda activate {env} \n \
               export MKL_NUM_THREADS=1 \n \
               export NUMEXPR_NUM_THREADS=1 \n \
               export OMP_NUM_THREADS=1 \n \
               export OPENBLAS_NUM_THREADS=1 \n \
               pwd \n \
               nvidia-smi \n '

# EDU slurm config details https://slurm.schedmd.com/pdfs/summary.pdf

"""
values: list of categorical possibilities
value: single possible value
"""

"""
    NB  cmd_line_arg overwrite cfg_arg 
    NB  None: Single run iterate always, 
        Grid/Random/Bayes: Iterate on first call (sweep_cfg), 
        Custom: Iterate on first call 
        
    write:  finds the variables from dict in this cfg, replaces, and writes new cfg
    EDU     regex cheatsheet https://medium.com/factory-mind/regex-tutorial-a-simple-cheatsheet-by-examples-649dc1c3f285
        """

sweep = dict(

)

slurm_cfg = dict(
    mail_type     = 'FAIL',
    partition     ='sm3090',
    nodes         = 1,                # n_node
    ntasks        = 8,                # n_cpu
    cpus_per_task = 1,     
    time          = '0-12:00:00',     # D-HH:MM:SS
    gres          = 'gpu:RTX3090:1',
)

protected = dict(

)

paths = dict(

)

class Cfg(wClass):
    
    seed:               int         = 808017424     # grr
    iterate_exp_name:   bool        = False
    sweep:              dict        = sweep

    project_dir:        Path        = ''
    server_project_dir: Path        = ''

    server:             str         = 'server_id'   # SERVER
    user:               str         = 'user_id'     # SERVER
    env:                str         = ''            # CONDA ENV
    entity:             str         = entity
    job_type:           str         = 'training'
    git_remote:         str         = 'origin'
    git_main:           str         = 'main'

    data_path:          Path        = '~/data/a_data_file'
    run_path:           Path        = project_dir / 'run.py'
    project_exp_dir:    Path        = project_dir / 'exp'

    exp_name:           str         = 'junk'
    exp_id:             str         = gen_alphanum(n=7)
    exp_path:           Path        = project_exp_dir / exp_name / exp_id

    commit_id:          str         = git_commit_id()

    dtype:              str         = 'f32'
    n_step:             int         = 100
    b_size:             int         = 32
    lr:                 float       = 0.001

    n_layer:            int         = 3
    af:                 str         = 'tanh'    # activation function

    log_metric_step:    int         = 100
    log_state_step:     int         = 1000

    n_device:           int         = count_gpu()
    slurm_cfg:          dict        = dict(SlurmCfg(job_name=exp_name))
    sbatch_cfg:         str         = sbatch_cfg.format(env)

    def __init__(self, *, setup=True, protected=['n_device', 'sweep', 'sbatch_cfg'], **kwarg):
        super.__init__(self, kwarg | get_sys_arg())

        if setup:
            if self.sweep: # empty dictionaries bool to False
                self.exp_path = self.exp_path.parent # sweep cfg lives in dir above exps 
                copyfile(__file__, self.exp_path)

            if not self.sweep:
                
                with open(self.exp_path, 'r') as f:
                    line = f.readlines()
                
                for name, val in self.dict.items():              
                    if not (name in protected):
                        for l in line:
                            if re.search('class Sweep', l):   # Don't edit the sweep field
                                l = next(l)
                                l = '\t' + 'pass'
                                while re.search('^\s', l):  # matches whitespace at start
                                    l = next(l)
                                    l = ['']
                            elif re.search(name, l) and (m:=re.search('= *[^(#|\r\n|\r|\n)]*', l)):
                                lhs, rhs = m.span()
                                l = [l[:lhs], f' {val} ', l[rhs:]]
                
                with open(self.exp_path, 'w') as f:
                    f.writelines(line)


'''PROCESS
SUBMIT LOCALLY
python run.py

SUBMIT REMOTELY
python submit.py --config_path cfg_path
- gets the config for slurm from config und das ist das 
'''

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