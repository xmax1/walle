

from pathlib import Path
from typing import Any
from walle.bureaucrat import gen_alphanum
from walle.submit import count_gpu, get_sys_arg
from walle.wutils import Cfg

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
slurm_cfg = {
    'mail_type'     : 'FAIL',
    'partition'     : 'sm3090',
    'nodes'         : 1, # n_node
    'ntasks'        : 8, # n_cpu
    'cpus_per_task' : 1, 
    'time'          : '0-12:00:00', # D-HH:MM:SS
    'gres'          : 'gpu:RTX3090:1',
    'job_name'      : 'science',
}

class Sweep:
    pass 

# alternately use wandbs explicit notatio


def cfg() -> Cfg:
    """
    NB  cmd_line_arg overwrite cfg_arg 
    SWEEP EXAMPLE
    arg_name: Sweep = [val1, val2, ...]
    NB  works if val are list 
    NB  y: list = [] is not recognised as Sweep but y: Sweep = [] is recognised as list """

    project_dir:        Path    = ''
    server_project_dir: Path    = ''
    data_path:          Path    = '~/data/a_data_file'
    run_path:           Path    = project_dir / 'run.py'
    exp_id:             str     = 'junk'
    
    server:             str     = 'server_id'   # SERVER
    user:               str     = 'user_id'     # SERVER
    env:                str     = ''         # CONDA ENV
    
    git_remote:         str     = 'origin'
    git_main:           str     = 'main'
    
    entity:             str     = entity
    job_type:           str     = 'training'
    
    slurm_cfg:          dict    = slurm_cfg
    sbatch_cfg:         str     = sbatch_cfg.format(env)

    commit_id:          str     = commit_id
    n_device:           int     = count_gpu()

    project_exp_dir:    Path    = project_dir / 'exp'
    project_cfg_dir:    Path    = project_dir / 'cfg'
    exp_name:           str     = gen_alphanum(n=7)
    exp_path:           Path    = project_exp_dir / exp_id / exp_name

    dtype:              str     = 'f32'
    n_step:             int     = 100
    b_size:             int     = 32
    lr:                 float   = 0.001

    n_layer:            int     = 3
    af:                 str     = 'tanh'    # activation function

    log_metric_step:    int     = 100
    log_state_step:     int     = 1000
 
    cfg_arg = locals()
    cmd_line_arg = get_sys_arg()
    return Cfg(cfg_arg | cmd_line_arg )  # cmd line overwrites cfg

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