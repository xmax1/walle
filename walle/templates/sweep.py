import wandb
from pyfig import pyfig
from wutils import SubClass

class sweep:
    method: str = 'random'
    name: str = 'sweep'
    
    with SubClass() as metric:
        goal: str = 'minimize'
        name: str = 'validation_loss'

    with SubClass() as parameters:
        batch_size: dict = {'values': [16, 32, 64]}
        epoch: dict = {'values': [5, 10, 15]}
        lr: dict = {'max': 0.1, 'min': 0.0001}
     
c = pyfig(cfg_path='', create=True, iterate=False, sweep=sweep) # This is the base config

sweep_id = wandb.sweep(
    env     = f'conda activate {c.env};',
    sweep   = c.sweep, 
    program = c.wandb.run_path,
    project = c.wandb.project,
)

# run = wandb.init(  # not needed for sweep
#     entity=c.entity,
#     project=c.project_dir.name,
#     job_type=c.job_type,
#     cfg=c.todict(),
# )

# 🐝 Step 2: Define sweep config
sweep_cfg = {
    'program': '', 
    'method' : 'random',   # grid, random, bayes
    'name': 'sweep',
    'metric': {
        'goal': 'minimise', 'name': 'loss'
    },
    'parameters': 
    {
        'batch_size': {'values': [16, 32, 64]},
        'epochs': {'values': [5, 10, 15]},
        'lr': {'max': 0.1, 'min': 0.0001}
    }
}

""" default cmd line format 
command:
  - ${env}   # activates /usr/bin/env
  - ${interpreter}
  - ${program}
  - ${args}

/usr/bin/env python ${program} --param1=value1 --param2=value2
"""


# program
# (required) Training script to run.
# method
# (required) Specify the .
# parameters
# (required) Specify  bounds to search.
# name
# The name of the sweep, displayed in the W&B UI.
# description
# Text description of the sweep.
# metric
# Specify the metric to optimize (only used by certain search strategies and stopping criteria).
# early_terminate
# Specify any .
# command
# Specify for invoking and passing arguments to the training script.
# project
# Specify the project for this sweep.
# entity
# Specify the entity for this sweep.

wandb.agent(sweep_id, function=main, count=4)

