import sys
from pathlib import Path
from walle.bureaucrat import mkdir, gen_alphanum
from walle.submit import count_gpu, get_sys_arg, git_commit_id, run_cmd
from simple_slurm import Slurm

class Wandb:
    entity:             str     = ''            # wandb entity
    job_type:           str     = 'training'
    project:            str     = property(lambda _: c.project)
    sweep_id:           str     = ''

slurm = Slurm(
    output          = TMP / 'o-%j.out',
    error           = TMP / 'e-%j.err',
    mail_type       = 'FAIL',
    partition       ='sm3090',
    nodes           = 1,                # n_node
    ntasks          = 8,                # n_cpu
    cpus_per_task   = 1,     
    time            = '0-12:00:00',     # D-HH:MM:SS
    gres            = 'gpu:RTX3090:1',
    job_name        = property(lambda _: c.exp_name),  # this does not call the instance it is in
)

sbatch = f"""
    module purge 
    source ~/.bashrc 
    module load GCC 
    module load CUDA/11.4.1 
    module load cuDNN/8.2.2.26-CUDA-11.4.1 
    conda activate {c.env} 
    export MKL_NUM_THREADS=1 
    export NUMEXPR_NUM_THREADS=1 
    export OMP_NUM_THREADS=1 
    export OPENBLAS_NUM_THREADS=1
    pwd
    nvidia-smi
"""

class Pyfig:

    sys_arg: dict = get_sys_arg()

    exp_name:           str     = exp_name
    exp_id:             str     = None
    exp_path:           Path    = property(lambda c: c.project_exp_dir / c.exp_name)
    run_path:           Path    = property(lambda c: c.project_dir / 'run.py')
    run:                bool    = 'run'  # run, sweep_lord, sweep_agent

    seed:               int     = 808017424     # grr
    n_device:           int     = property(count_gpu)
    commit_id:          str     = git_commit_id()

    class Sweep:  # Inside just for readability
        ...
        # method: str = 'random'
        # name: str = 'sweep'
        # with SubClass() as metric:
        #     goal: str = 'minimize'
        #     name: str = 'validation_loss'
        # with SubClass() as parameters:
        #     batch_size: dict = {'values': [16, 32, 64]}
        #     epoch: dict = {'values': [5, 10, 15]}
        #     lr: dict = {'max': 0.1, 'min': 0.0001}

    dtype:              str     = 'f32'
    n_step:             int     = 100
    b_size:             int     = 32
    lr:                 float   = 0.001

    n_layer:            int     = 3
    af:                 str     = 'tanh'    # activation function

    log_metric_step:    int     = 100
    log_state_step:     int     = 1000         # wandb entity

    project_dir:        Path    = Path().absolute().parent
    project:            str     = property(lambda _: c.project_dir.name)
    project_exp_dir:    Path    = property(lambda _: c.project_dir / 'exp')
    project_cfg_dir:    Path    = property(lambda _: c.project_dir / 'cfg')
    server_project_dir: Path    = property(lambda _: c.project_dir)

    data_path:          Path    = Path('~/data/a_data_file')
    server:             str     = 'server_id'   # SERVER
    user:               str     = 'user_id'     # SERVER
    env:                str     = 'dex'         # CONDA ENV
    git_remote:         str     = 'origin'
    git_branch:           str   = 'main'

    wandb = Wandb()
    slurm = Slurm()
    sweep = Sweep()
    
    def __init__(self) -> None:
        self.__dict__ |= {self.sys_arg}

    @property
    def dict(self,):
        return self._dictify(self)

    def parse_args(self, _i=0, _d={}):
        while _i<(len(arg:=sys.argv[1:])-1):
            k, v = arg[_i], arg[(_i:=_i+1)]
            flag0, flag1 = '-' == k[0], '-' == v[0]
            k, v = k.lstrip('-'), v.lstrip('-') 
            if flag0 and flag1:  # --store_true action
                _d[k] = True
            else:
                _d[v] = type(self.dict[k])(v)
                _i += 1

    def _dictify(self, cls):
        d = cls.__dict__
        d = self._filter_attr(d)
        for k, v in d.items():
            if isinstance(v, Slurm | Wandb):  # sweep doesn't need to be dictified
                d[k] = self._dictify(v)
        return d

    def set(self, cls, var: dict, _set=0):
        d = cls.__dict__
        for k,v in var.items():
            if (k in self.__dict__):
                self.__dict__[k] = v
                _set += 1
            else:
                for k, v in d.items():
                    if isinstance(v, Slurm | Wandb):
                        self.set(v)
        return (_set == len(var))

    @staticmethod
    def _filter_attr(cls: object):
        return {k:v for k,v in cls.__dict__.items() if (not k[0] == '_')}

    @property
    def n_sweep(self, _n=1):
        for k, v in self.sweep.parameters:
            _n *= len(v.get('values', []))
            # _n += len(v.get('values', []))  # other methods for probabilistic
        return _n

    def run_slurm(self, sweep_id='', agent=False, exp_id=False):
        sweep_agent = agent * ' --run sweep_agent '
        exp_id = exp_id * f' --exp_id {gen_alphanum(7)} '
        sweep_id = bool(sweep_id) * f'--sweep_id {sweep_id}'
        cmd = f'python -u {self.run_path} ' + sweep_id + sweep_agent + exp_id
        self.slurm.sbatch(
            sbatch + 
            f'out_dir={(mkdir(self.exp_path)/"out")} \n \
            {cmd} | tee $out_dir/py.out \n \
            {mv_cmd} \n \
            date "+%B %V %T.%3N" '
        )
        


c = Pyfig()

# aesthetics > practicality mk
TMP = mkdir('./tmp/out')
mv_cmd = f'mv {TMP}/o-$SLURM_JOB_ID.out {TMP}/e-$SLURM_JOB_ID.err $out_dir'