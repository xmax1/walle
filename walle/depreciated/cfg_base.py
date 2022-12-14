import sys
from pathlib import Path
from walle.bureaucrat import mkdir, gen_alphanum
from walle.submit import count_gpu, get_sys_arg, git_commit_id
from simple_slurm import Slurm
from functools import reduce

TMP = mkdir('./tmp/out')

sweep = dict(
    method = 'random',
    name = 'sweep',
    metrics = dict(
        goal = 'minimize',
        name = 'validation_loss',
    ),
    parameters = {}
    # parameters = dict(
    #     batch_size = {'values': [16, 32, 64]},
    #     epoch = {'values': [5, 10, 15]},
    #     lr = {'max': 0.1, 'min': 0.0001},
    # ),
)

class Pyfig:

    sys_arg: dict = sys.argv[1:]

    seed:               int     = 808017424         # grr
    env:                str     = 'dex'             # CONDA ENV
    commit_id:          str     = git_commit_id()
    n_device:           int     = property(lambda _: count_gpu())
    job_type:           str     = 'training'

    exp_name:           str     = exp_name
    run_path:           Path    = property(lambda _: _.project_dir / 'run.py')
    _exp_id:            str     = ''
    
    sweep_id:          str      = ''
    sweep = sweep
    n_sweep: int = reduce(lambda i0,i1: i0*i1, [len(v) for v in sweep['parameters'].values()]) if sweep['parameters'] else 0

    dtype:              str     = 'f32'
    n_step:             int     = 100
    b_size:             int     = 32
    lr:                 float   = 0.001

    n_layer:            int     = 3
    af:                 str     = 'tanh'    # activation function

    log_metric_step:    int     = 100
    log_state_step:     int     = 1000         # wandb entity

    project_dir:        Path    = Path().absolute().parent
    server_project_dir: Path    = property(lambda _: _.project_dir)

    project:            str     = property(lambda _: _.project_dir.name)
    project_exp_dir:    Path    = property(lambda _: _.project_dir / 'exp')
    project_cfg_dir:    Path    = property(lambda _: _.project_dir / 'cfg')
    exp_path:           Path    = property(lambda _: Path(_.project_exp_dir, _.exp_name, _.exp_id))

    data_path:          Path    = Path('~/data/a_data_file')
    server:             str     = 'server_id'   # SERVER
    user:               str     = 'user_id'     # SERVER
    entity:             str     = ''            # WANDB entity
    git_remote:         str     = 'origin'
    git_branch:         str     = 'main'

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
        job_name        = property(lambda _: _.exp_name),  # this does not call the instance it is in
    )

    sbatch = property(lambda _: f"""
        module purge 
        source ~/.bashrc 
        module load GCC 
        module load CUDA/11.4.1 
        module load cuDNN/8.2.2.26-CUDA-11.4.1 
        conda activate {_.env} 
        export MKL_NUM_THREADS=1 
        export NUMEXPR_NUM_THREADS=1 
        export OMP_NUM_THREADS=1 
        export OPENBLAS_NUM_THREADS=1
        pwd
        nvidia-smi
        mv_cmd = f'mv {TMP}/o-$SLURM_JOB_ID.out {TMP}/e-$SLURM_JOB_ID.err $out_dir'
    """
    )

    @property
    def dict(self,):
        d = self._dict_from_cls(self)
        for k,v in d.items():
            if isinstance(v, Slurm):
                d[k] = self._dict_from_cls(v)
        return d
        
    @staticmethod
    def _dict_from_cls(cls): # GETS ALL ATTRS AND PROPERTIES 
        ps = {k: getattr(cls, k) for k,v in super.__dict__.items() 
                    if isinstance(v, property) and not k=='dict'}
        return cls.__dict__ | ps

    def update_from_sys_arg(self):
        booleans = [arg for i, arg in self.sys_arg if self.sys_arg[i].startswith('-') and self.sys_arg[i+1].startswith('-')]
        d = {b:True for b in booleans}
        sys_arg = iter([arg for arg in self.sys_arg if not arg in booleans])
        for k,v in sys_arg:
            d[k] = v
        self.update(d)

    def update(self, d: dict):
        for k,v in d.items():
            assert self._update(self, self, k, v)

    def _update(self, cls, k, v):
        if k in cls.__dict__.keys():
            cls.__dict__[k] = type(cls.__dict__[k])(v)
            return True
        for cls_v in cls.__dict__.values():
            if isinstance(cls_v, Slurm):
                self._update(cls_v, k, v)
        return False

    def run_slurm(self,):
        sweep_id = bool(self.sweep_id) * f'--sweep_id {self.sweep_id}'
        cmd = f'python -u {self.run_path} --exp_id {self._exp_id}' + sweep_id
        self.slurm.sbatch(
            self.sbatch + 
            f'out_dir={(mkdir(self.exp_path/"out"))} \n \
            {cmd} | tee $out_dir/py.out \n \
            date "+%B %V %T.%3N" '
        )