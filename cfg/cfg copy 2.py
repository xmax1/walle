from pathlib import Path
import re
from shutil import copyfile
from typing import Any
from walle.bureaucrat import gen_alphanum, iterate_folder, mkdir
from walle.submit import count_gpu, get_sys_arg, git_commit_id

this_path = Path(__file__)

class wContext:
    def __init__(self, protect:bool=False):
        self.protect = protect
    def __enter__(self):
        self._var = set(globals())
        return self
    def __exit__(self, *args):
        self.k = [self.protect*'_'+k for k in list(set(globals()) - self._var)]

with wContext(protect=True) as slurm_cfg:
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



class Cfg:

    seed:               int         = 808017424     # grr

    project_dir:        Path        = ''
    server_project_dir: Path        = ''
    data_path:          Path        = Path('~/data/a_data_file')
    project_exp_dir:    Path        = project_dir / 'exp'
    run_path:           Path        = project_dir / 'run.py'

    exp_name:           str         = 'junk'
    exp_path:           Path        = project_exp_dir / exp_name

    dtype:              str         = 'f32'
    n_step:             int         = 100
    b_size:             int         = 32
    lr:                 float       = 0.001

    n_layer:            int         = 3
    af:                 str         = 'tanh'    # activation function

    log_metric_step:    int         = 100
    log_state_step:     int         = 1000

    slurm = dict(
        mail_type                   = 'FAIL',
        partition                   ='sm3090',
        nodes                       = 1,                # n_node
        ntasks                      = 8,                # n_cpu
        cpus_per_task               = 1,     
        time                        = '0-12:00:00',     # D-HH:MM:SS
        gres                        = 'gpu:RTX3090:1',
    )

    project = dict(
        server                      = 'server_id',   # SERVER
        user                        = 'user_id',     # SERVER
        env                         = '',            # CONDA ENV
        entity                      = '',            # wandb entity
        job_type                    = 'training',
        git_remote                  = 'origin',
        git_main                    = 'main',
        commit_id                   = git_commit_id(),
    )

    n_device:           int         = count_gpu()
    slurm_cfg:          dict        = slurm_cfg | dict(job_name=exp_name)
    sbatch_cfg:         str         = sbatch_cfg.format(project['env'])

    sweep = dict(
    
    )  # END

    def __init__(self, *, setup=True, iterate_exp_name=True, **kwarg):
        new_arg = kwarg | get_sys_arg()        
        
        self.__dict__.update(new_arg)

        if iterate_exp_name:
            self.exp_path = iterate_folder(self.project_exp_dir/self.exp_name)
        
        if not self.sweep: # bool(empty dictionary) = False
            self.exp_path /= gen_alphanum(n=7)

        if setup:
            write_d = {k:v for k,v in self.__dict__ if k not in ['commit_id', 'n_device']}
            save_pyfig(__file__, self.exp_path, write_d)

def save_pyfig(source: Path, target: Path, write_d: dict):    
    n_lines_changed = 0

    with open(source, 'r') as f:
        l_source = f.readlines()
    
    with open(mkdir(target), 'w') as f:
        
        for l in l_source:
            if re.search('sweep *= *dict', l):   
                while not re.search('END', l):  #  '^\s' matches whitespace at start
                    f.writelines(l)  
                    l = next(l_source)
            
            for name, val in write_d.items():
                if re.search(name, l):
                    lhs, rhs = re.search('= *[^(#|\r\n|\r|\n)]*', l).span()
                    l = [l[:lhs], f' {val} ', l[rhs:]]
                    n_lines_changed += 1
        
            f.writelines(l)
    assert n_lines_changed == len(write_d)