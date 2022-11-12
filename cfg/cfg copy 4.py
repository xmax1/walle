from pathlib import Path
from walle.submit import count_gpu, git_commit_id, get_sys_arg
from walle.pyfig import wContext

__start_pyfig = set(globals())

exp_name:           str     = 'junk'

server:             str     = 'server_id'   # SERVER
user:               str     = 'user_id'     # SERVER
env:                str     = 'dex'         # CONDA ENV
entity:             str     = ''            # wandb entity
job_type:           str     = 'training'
git_remote:         str     = 'origin'
git_main:           str     = 'main'

data_path:          Path    = Path('~/data/a_data_file')

with wContext(protect=True):
    project_dir:        str    =  Path(r'C:\Users\max\OneDrive\sisy\walle').absolute()
    server_project_dir: Path    = ''
    project_exp_dir:    Path    = project_dir / 'exp'
    exp_path:           Path    = project_exp_dir / exp_name

    n_device:           int         = count_gpu()
    source_path:        Path        = Path(__file__)
    slurm_body: str  = \
        f'module purge \n \
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

with wContext() as slurm:
    mail_type:      str     = 'FAIL'
    partition:      str     ='sm3090'
    nodes:          str     = 1                # n_node
    ntasks:         str     = 8                # n_cpu
    cpus_per_task:  str     = 1     
    time:           str     = '0-12:00:00'     # D-HH:MM:SS
    gres:           str     = 'gpu:RTX3090:1'
    job_name:       str     = exp_name

run_path:           Path    = project_dir / 'run.py'
commit_id:          str     = git_commit_id(cwd=project_dir)
seed:               int     = 808017424     # grr

dtype:              str     = 'f32'
n_step:             int     = 100
b_size:             int     = 32
lr:                 float   = 0.001

n_layer:            int     = 3
af:                 str     = 'tanh'    # activation function

log_metric_step:    int     = 100
log_state_step:     int     = 1000

__end_pyfig = set(globals()) 

Config = {k:v for k,v in globals().items() if k in list(__start_pyfig - __end_pyfig)} # Filter builtins

Config['sys_arg'] = get_sys_arg()

subclasses = {k:[v_ for v_ in v.k if not k in v] for k,v in Config.items() if isinstance(v, wContext)}
Config = {k:v for k,v in Config.items() if not '__' in k} | subclasses | Config['sys_arg']

