

import wandb
from pathlib import Path
from paths import experiments_dir
from tqdm import tqdm, trange
from time import time

from walle.config import collect_args, create_types


args = collect_args()
args = create_types()
workdir = str(Path(experiments_dir) / args['exp_name'])
sample_dir = Path(workdir, "samples")

# from utils import to_wandb_config
# from configs import oxford102
# cfg = oxford102.get_config()

wandb.init(
    entity=cfg.wandb.entity,
    project=cfg.wandb.project,
    job_type=cfg.wandb.job_type,
    cfg=to_wandb_config(cfg)
)

num_steps = cfg.training.num_train_steps

for step, batch in zip(tqdm(range(1, num_steps)), train_iter):
    
    
    if cfg.training.get('log_every_steps'):
        
    
        if (step + 1) % cfg.training.log_every_steps == 0:
            d, t0 = time() - t0, time() 
            
            summary = {}  # these will be logged, dict format

            wandb.log({
                    "train/step": step, 
                    **summary
                })
    
    # Save a checkpoint periodically and generate samples.
    if (step + 1) % cfg.training.save_and_sample_every == 0 or step + 1 == num_steps:

        # utils.wandb_log_image(samples, step+1)

        ### LOG MODEL
        if step + 1 == num_steps and cfg.wandb.log_model:
            artifact = wandb.Artifact(name=f"model-{wandb.run.id}", type="")
            artifact.add_file( f"{workdir}/checkpoint_{step}")
            wandb.run.log_artifact(artifact)
