import wandb
from walle.pyfig import Pyfig
from walle.bureaucrat import remove_path
# run_cmd(f'export WANDB_DIR={c.exp_path}', cwd='.')  # set wandb before the path changes

c = Pyfig()

c.sweep = dict(
    method = 'random',
    name = 'sweep',
    metrics = dict(
        goal = 'minimize',
        name = 'validation_loss',
    ),
    parameters = dict(
        batch_size = {'values': [16, 32, 64]},
        epoch = {'values': [5, 10, 15]},
        lr = {'max': 0.1, 'min': 0.0001},
    ),
)

c.sweep_id = wandb.sweep(
    env     = f'conda activate {c.env};',
    sweep   = c.sweep, 
    program = c.run_path,
    project = c.project,
    name    = c.exp_name,
    run_cap = c.n_sweep
)

[c.run_slurm() for _ in range(c.n_sweep)]

if c.exp_path.exists():
    remove_path(c.exp_path)


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
