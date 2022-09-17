
import wandb

from utils import collect_data_dict, generate_cfg


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
            wandb_logs = {'loss': loss}
            wandb.log(wandb_logs)

        if it % c.log_model_it == 0:


    summary = {'best_it': exp_stats}
    for k, v in summary:
        run.summary[k] = v

    run.finish()



def compute_pair_correlation():



    # exp_stat = {'mean': np.mean(x)}


    exp_stats = collect_data_dict(exp_stats, exp_stat)