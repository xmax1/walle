import sys
from pathlib import Path
from walle.submit import count_gpu, get_sys_arg, git_commit_id

class SubClass:
    """
    %reset -f if testing in jupyter, because globals can only tell if a variable has CHANGED"""
    def __init__(self):
        pass
    def __enter__(self):
        self.__var = dict(globals())
        return self
    def __exit__(self, *args):
        _g = {k:v for k,v in dict(globals()).items() if not ((k in self.__var) or ('__' in k))}
        for k, v in _g.items():
            if not isinstance(v, SubClass):
                self.__dict__[k] = v
    
class Pyfig:

    sys_arg: dict = get_sys_arg()

    exp_name:           str     = exp_name
    exp_path:           Path    = property(lambda self: self.project_exp_dir / self.exp_name)
    run_path:           Path    = property(lambda self: self.project_dir / 'run.py')

    seed:               int     = 808017424     # grr
    n_device:           int     = property(count_gpu)
    commit_id:          str     = git_commit_id()

    with SubClass() as sweep:
        var_1 = ... # wandb structure

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

    with SubClass() as wandb:
        entity:             str     = ''            # wandb entity
        job_type:           str     = 'training'

    with SubClass() as slurm:
        mail_type:      str     = 'FAIL'
        partition:      str     ='sm3090'
        nodes:          str     = 1                # n_node
        ntasks:         str     = 8                # n_cpu
        cpus_per_task:  str     = 1     
        time:           str     = '0-12:00:00'     # D-HH:MM:SS
        gres:           str     = 'gpu:RTX3090:1'
        job_name:       str     = property(lambda _: c.exp_name)  # this does not call the instance it is in
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

    project_dir:        Path    = Path().absolute().parent
    project_exp_dir:    Path    = property(lambda self: self.project_dir / 'exp')
    project_cfg_dir:    Path    = property(lambda self: self.project_dir / 'cfg')
    server_project_dir: Path    = property(lambda self: self.project_dir)

    data_path:          Path    = Path('~/data/a_data_file')
    server:             str     = 'server_id'   # SERVER
    user:               str     = 'user_id'     # SERVER
    env:                str     = 'dex'         # CONDA ENV
    git_remote:         str     = 'origin'
    git_main:           str     = 'main'

    def __init__(self) -> None:
        self.__dict__ |= {self.sys_arg}

    @property
    def dict(self,):
        d = self._filter_attr(self)
        for k, v in d.items():
            if isinstance(v, SubClass):
                d[k] = self._filter_attr(v)
        del d['dict']
        return d

    @staticmethod
    def _filter_attr(cls: object):
        return {k:v for k,v in cls.__dict__.items() if (not k[0] == '_')}

    @staticmethod
    def parse_args(self, _i=0, _d={}):
        arg = sys.argv[1:]
        while _i<5000:
            k = arg[_i]
            v = arg[(_i:=_i+1)]
            
            if '-' == k[0] and '-' == v[0]:  # --store_true action
                _d[k] = True
            else:
                _d[v] = type(self.dict[k])(v)
                _i += 1

            if _i == len(arg):
                break
            
c = Pyfig()