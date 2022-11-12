from pathlib import Path
from walle.submit import count_gpu, get_sys_arg, git_commit_id

class SubClass:
    def __init__(self, name):
        self.__name__ = name
    def __enter__(self):
        self._var = set(globals())
    def __exit__(self, *args):
        keys = [k for k in list(set(globals()) - self._var)]
        for k in keys:
            setattr(self, k, vars()[k])

class Pyfig:

    sys_arg: dict = get_sys_arg()

    exp_name:           str     = exp_name
    seed:               int     = 808017424     # grr
    n_device:           int     = property(count_gpu)
    commit_id:          str     = git_commit_id()

    dtype:              str     = 'f32'
    n_step:             int     = 100
    b_size:             int     = 32
    lr:                 float   = 0.001

    n_layer:            int     = 3
    af:                 str     = 'tanh'    # activation function

    log_metric_step:    int     = 100
    log_state_step:     int     = 1000
    entity:             str     = ''            # wandb entity
    
    job_type:           str     = 'training'

    with SubClass('wandb'):
        entity:             str     = ''            # wandb entity
        job_type:           str     = 'training'

    with SubClass('slurm'):
        mail_type:      str     = 'FAIL'
        partition:      str     ='sm3090'
        nodes:          str     = 1                # n_node
        ntasks:         str     = 8                # n_cpu
        cpus_per_task:  str     = 1     
        time:           str     = '0-12:00:00'     # D-HH:MM:SS
        gres:           str     = 'gpu:RTX3090:1'
        job_name:       str     = property(lambda _: Pyfig.exp_name)
        slurm_body: str = property( lambda _: \
            f'module purge \n \
            source ~/.bashrc \n \
            module load GCC \n \
            module load CUDA/11.4.1 \n \
            module load cuDNN/8.2.2.26-CUDA-11.4.1 \n \
            conda activate {c.env} \n \
            export MKL_NUM_THREADS=1 \n \
            export NUMEXPR_NUM_THREADS=1 \n \
            export OMP_NUM_THREADS=1 \n \
            export OPENBLAS_NUM_THREADS=1 \n \
            pwd \n \
            nvidia-smi \n '
        ) 

    project_dir:        str    =  Path().absolute().parent
    server_project_dir: Path    = property(lambda self: self.project_dir)
    data_path:          Path    = Path('~/data/a_data_file')
    server:             str     = 'server_id'   # SERVER
    user:               str     = 'user_id'     # SERVER
    env:                str     = 'dex'         # CONDA ENV
    git_remote:         str     = 'origin'
    git_main:           str     = 'main'

    @property
    def dict(self,):
        d = self._filter_attr(self)
        for k, v in d.items():
            if isinstance(v, SubClass):
                d[k] = self._filter_attr(v)
        del d['dict']
        return d

    @staticmethod
    def _filter_attr(cls):
        return {k:v for k,v in type(cls).__dict__.items() if (not k[0] == '_')}

c = Pyfig()