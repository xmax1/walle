# Journey
- Decide on sweep or single run

## Sweep
- provide user with wandb configuration tools
- write a tosweep tool that converts everything to the structure needed for wandb
- create cfg tool overwrites variables that change
- at the end of a cfg init, write the sweep cfg to the head

- wandb.sweep runs remote execution with these parameters
    - where does the wandb sweep file go? 
    - if wandb runs slurm then run thinks individual sweep so need method for turning wandb off

## Sweep 
- How to identify sweep variables - from wandb. 
    - Define the sweep in the config.py with Sweep type
    - Write function to extract sweep
    - wandb turns off if is a sweep? 


## 




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