
from pyexpat import model
import wandb

from utils import collect_data_dict, generate_cfg, commit, save_pk

'''
- workspace
    - experiments
        - sweep_name
            - sweep_cfg.yaml  # move by slurm
            - defining_features_idx  # run_dir
                - out
                - state
                    - i{i}.pk
                        - models
                        - opt_state
                        - results
                        - other objets
                - plot.png
                - cfg.yaml
                - cfg.pk
'''

def run_vmc(cfg_path: str | None = None):

    c = generate_cfg(cfg_path)

    run = wandb.init(
        entity = c.entity,
        project = c.project,
        group = c.sweep_name,
        mode = c.wandb,
        config = c.dict
    )

    exp_stats = {}
    for it in c.n_it:
        
        if it % c.log_metric_it == 0:
            wandb_logs = {
                'loss': None
            }
            wandb.log(wandb_logs)

        if it % c.log_state_it == 0:
            state = {
                'model': None,
                'opt': None,
                'results': None,
                'walkers': None,
            } 
            save_pk(state, c.state_file.format(it))


    summary = {
        'best_it': exp_stats
    }
    
    for k, v in summary:
        run.summary[k] = v

    run.finish()



def compute_pair_correlation():



    # exp_stat = {'mean': np.mean(x)}


    exp_stats = collect_data_dict(exp_stats, exp_stat)


if __name__ == '__main__':

    