import wandb
from walle.pyfig import pyfig
import numpy as np

c = pyfig(cfg_path='', create=True, iterate=False, sweep=None) # This is the base config

if c.run == 'sweep_agent':
    wandb.agent(c.sweep_id, count=1)  # function=main

run = wandb.init(  # not needed for sweep
    entity=c.wandb.entity,
    project=c.project,
    job_type=c.job_type,
    cfg=c.dict,  # over-ridden in sweep case
)

if run.config:
    c.update(run.config)

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
