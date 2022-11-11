import wandb
from submit import Cfg

# pass wandb a sweep dict 
# how does wandb execute the file? Cmd line args? 
    # wandb.init command option defines how args passed
# wandb.log the metric needing to be optimized
# wandb.init option description can be the REQUIRED hypothesis

### SWEEP AND CONFIG
# change config to Cfg class (remove from wutils)
# load module and create class for any type of loading
# keep wClass cool things
# tosweep exports ONLY sweep variables (ones containing the sweep keys from wandb) to parameter and sets up config as required
# 


c = Cfg() # This is the base config

sweep_id = wandb.sweep(
    env     = f'conda activate {c.env};',
    sweep   = c.tosweep(), 
    program = c.run_path,
    project ='my-first-sweep',
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

