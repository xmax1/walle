import wandb
from walle.pyfig import pyfig
from walle.submit import submit_sweep_agent_all
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

match c.run:
    case 'sweep_lord':
        c.sweep_id = wandb.sweep(
            env     = f'conda activate {c.env};',
            sweep   = c.sweep, 
            program = c.run_path,
            project = c.project,
            name    = c.exp_name,
            run_cap = c.n_sweep
        )
        for _s in range(c.n_sweep):
            c.submit_slurm(agent=True, exp_id=True)
        exit('Run sweep')

    case 'sweep_agent':
        wandb.agent(c.sweep_id, count=1)  # function=main

    case 'run' | 'sweep_agent':
        
        run = wandb.init(  # not needed for sweep
            entity=c.wandb.entity,
            project=c.project,
            job_type=c.job_type,
            cfg=c.dict,  # over-ridden in sweep case
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
