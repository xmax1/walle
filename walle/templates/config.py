

from pathlib import Path

from walle.bureaucrat import gen_alphanum, mkdir, iterate_folder
from wutils import Config
from walle.submit import  load_cfg, count_gpu, get_sys_arg, git_commit_id
import re

""" MODES
NB  if user calls remote submission, do we need a flag to understand 
- script 
- sweep
- script server 
- sweep server
- script push to server 
- sweep push to server
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

def create_config(cfg_path: Path, target_path: Path, d: dict):
    """" finds the variables from dict in this cfg, replaces, and writes new cfg
    EDU regex cheatsheet https://medium.com/factory-mind/regex-tutorial-a-simple-cheatsheet-by-examples-649dc1c3f285 
    NB  may be edge cases """
    with open(cfg_path, 'r') as f:
        line = f.readlines()
    n_replace = len(d)
    for name, val in d.items():
        for l in line:
            if re.search(name, l) and (m:=re.search('= *[^(#|\r\n|\r|\n)]*', l)):
                n_replace -= 1
                lhs, rhs = m.span()
                l = [l[:lhs], f' {val} ', l[rhs:]]
    assert n_replace == 0
    with open(target_path, 'w') as f:
        f.writelines(line)
    return None

def create_cfg(cfg_path: Path = None) -> Config:
    cmd_line_arg = get_sys_arg()
    if cfg_path is None:
        # USER/RUN/PROJECT VARIABLES
        project_dir:        Path    = '.'
        server_project_dir: Path    = '.'
        data_path:          Path    = '~/data/a_data_file'
        run_path:           Path    = project_dir/'run.py'
        exp_id:             str     = gen_alphanum(n=7)
        commit_id:          str     = git_commit_id()
        exp_name:           Path    = 'junk'
        seed:               int     = 808017424     # grr
        
        server:             str     = 'server_id'   # SERVER
        user:               str     = 'user_id'     # SERVER
        env:                str     = ''            # CONDA ENV
        
        git_remote:         str     = 'origin'
        git_main:           str     = 'main'
        
        entity:             str     = entity
        job_type:           str     = 'training'
        
        slurm_cfg:          dict    = slurm_cfg
        sbatch_cfg:         str     = sbatch_cfg.format(env)

        # OTHER
        commit_id:          str     = commit_id
        n_device:           int     = count_gpu()
    
        project_exp_dir:    Path    = project_dir / 'exp'
        project_cfg_dir:    Path    = project_dir / 'cfg'
        exp_path:           Path    = iterate_folder(project_exp_dir / exp_name) / exp_id

        dump_path:          Path   = mkdir(exp_path/ 'dump')

        dtype:              str     = 'f32'
        n_step:             int     = 100
        b_size:             int     = 32
        lr:                 float   = 0.001

        n_layer:            int     = 3
        af:                 str     = 'tanh'    # activation function

        log_metric_step:    int     = 100
        log_state_step:     int     = 1000

        cfg_arg = locals()

        # DOESNT OVERWRITE SECOND TIME
        overwrite = {'exp_id': exp_id, 'commit_id': commit_id} | cmd_line_arg
        create_config(__file__, exp_path/'config.py', overwrite)
        
        c = Config(cfg_arg | cmd_line_arg)  # TODO: check works in place. | is the union two dicts
    else:  
        ''' loads this file from the correct place, contains everything one might need for SCIENCE
        NB '''
        c = load_cfg(cfg_path)
    return c

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