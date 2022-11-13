# Journey
- All these exps assume loading cfg.cfg c
- Provide --cfg_path path for other config

## Run (local)
python run.py

## Run sweep (local)
- Change sweep configuration, either in the pyfig or in the script
python run.py 

## slurm
- server_cfg=FAB <cmd> to use project/_settings.py server config
- hierarchy of sweep config: defined in run.py > defined in pyfig

## Run sweep (slurm)
- fab submit "sweep.py --data_path <data_path>"
    - calls sweep.py
    - which sets up wandb instance
    - and submits slurm via Pyfig, with --sweep_id <id> --run sweep_agent --exp_id <random> options (sweep_agent True, exp_id True)

## Run (slurm)
- fab submit "run.py --data_path <data_path>"  # TODO HOW TO KNOW WHEN IT SUBMITS TO GPU?!
    - calls run.py
    - which sets up wandb instance
    - and submits slurm via Pyfig, with --run sweep_agent --exp_id <random> options (sweep_agent True, exp_id True)

python run.py <args>





# np.squeeze / np.array standardisation of stats needs to handle the edge case where no squeeze and be neater

# Any time you write a line of code
'''
- does the variable exist yet
- what is the shape of the array
- what is the type of the objects
- does the path exist
- 
'''

# create a safe append to dict function for this 
'''
- Make everything numpy 
- Don't fuck with the shapes
'''
# Type list
python internal : float, int, list, str, dict 
pathlib         : Path
numpy           : np.ndarray
pytorch/jax/tensorflow: used only in mod and jax_, torch_, tf_ utils and identified by 'shape' in dir(arr)
typing          : Any, Callable

# Tutorial for dum dums