import wandb
from pyfig import pyfig
from wutils import SubClass
from submit import submit_sweep

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

if c.sweep:
    # If sweep_id available, be sweep lord
    # sweep_id is the only hypam needed to supply to the server, the agent handles the config
    if c.sweep_id:
        wandb.agent(c.sweep_id, count=1)  # function=main
    else:
        c.sweep_id = wandb.sweep(
            env     = f'conda activate {c.env};',
            sweep   = c.sweep, 
            program = c.wandb.run_path,
            project = c.wandb.project,
            name    = c.exp_name,
            run_cap = c.n_sweep
        )
        submit_sweep(c)
        exit('Sweep submitted')

run = wandb.init(  # not needed for sweep
    entity=c.entity,
    project=c.project,
    job_type=c.job_type,
    cfg=c.dict,  # over-ridden in sweep case
)

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



# entity/project/sweep_ID
# wandb.agent(sweep_id=sweep_id, function=function_name)
# wandb.agent(sweep_id, count=count) count = 1
#
# -b
# Issue a warning when comparing bytes or bytearray with str or bytes with int. Issue an error when the option is given twice (-bb).


run_id = wandb.init(
    entity=c.wandb.entity,
    project=c.wandb.project,
    job_type=c.wandb.job_type,
    cfg=c.dict
)

def log_metric(
    *, 
    model  = None, 
    param  = None, 
    metric = []
):
    metric_fn = {
        'mse': lambda x: x,
        'l1_norm': lambda x, y: np.mean(np.abs(x - y))
    }
    for m in metric:
        metric_fn[m](param)

metric = ['loss', 'this_thing']

for step, batch in range(1, c.n_step+1):
    
    if c.log_metric_step % step == 0:
        metric = log_metric(model=model, param=param, metric=metric)
        wandb.log({
                'train/step': step, 
                **summary
        })
    
    if c.log_state_step % step == 0:
        artifact = wandb.Artifact(name=f'model-{wandb.run.id}', type='')
        artifact.add_file(c.exp_path / f'model_i{step}')
        wandb.run.log_artifact(artifact)
