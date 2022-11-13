import wandb
from walle.pyfig import pyfig
import numpy as np

class sweep:
    # run_cmd(f'export WANDB_DIR={c.exp_path}', cwd='.')  # set wandb before the path changes
    method: str = 'random'
    name: str = 'sweep'
    
    class metric:
        goal: str = 'minimize'
        name: str = 'validation_loss'

    class parameters:
        batch_size: dict = {'values': [16, 32, 64]}
        epoch: dict = {'values': [5, 10, 15]}
        lr: dict = {'max': 0.1, 'min': 0.0001}

c = pyfig(cfg_path='', create=True, iterate=False, sweep=None) # This is the base config

c.sweep_id = wandb.sweep(
    env     = f'conda activate {c.env};',
    sweep   = c.sweep, 
    program = c.run_path,
    project = c.project,
    name    = c.exp_name,
    run_cap = c.n_sweep
)
[c.submit_slurm(agent=True, exp_id=True, sweep_id=c.sweep_id) for _ in range(c.n_sweep)]

"""
TODO
make gpus available if local

NOTES
For runs that are not part of a sweep, the values of wandb.config are usually set by providing a dictionary 
to the config argument of wandb.init. During a sweep, however, any configuration information passed to wandb.init 
is instead treated as a default value, which might be over-ridden by the sweep.

command:
  - ${env}   # activates /usr/bin/env
  - ${interpreter}
  - ${program}
  - ${args}

/usr/bin/env python ${program} --param1=value1 --param2=value2
"""
