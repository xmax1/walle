# variables needed in the config file
- project paths
- commit_id

## issues
- variables need to be declared or explicitly written and are not globally known

## potential workaround
- edit the python file (non-standard but also, why not?)

# absolute project paths into the config
- Needed so when the config is copied 

## commit_id
- Referenced by the name of the code copy file

## Complete integration with wandb sweep
- provide options in the Cfg
- Can run the sweep script directly - porque no eh?? runfig!... 
- Set the variables then export tosweep

## Iterate now a flag grr
- Flag for no iterate
- Set iterate true in all cases

# local_project_path = server_project_path restriction
- Not clear what the potential issues are and simplifies workflow
