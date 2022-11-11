### HYPERPARAMETER OPTIMISATION SWEEP ###

# from walle.submit import get_sys_arg
from optuna import create_study, load_study
import optuna
from optuna.samplers import TPESampler
import sqlite3
from sqlite3 import Error
from pathlib import Path

db_path = Path('./tmp/db.db')

# study object defines where to dump, what to call it, and the sampler for the optimisation
# study = create_study(
#     study_name='',
#     storage=db_path, # does this need to be a database? 
#     sampler=TPESampler,
#     pruner=optuna.pruners.MedianPruner(),
#     direction="minimize",
# )

# conn = sqlite3.connect(db_path)
# conn.close()

# def create_connection(db_file):
#     """ create a database connection to a SQLite database """
#     conn = None
#     try:
        
#         print(sqlite3.version)
#     except Error as e:
#         print(e)
#     finally:
#         if conn:

def objective(trial):
    x = trial.suggest_float("x", -10, 10)
    return (x - 2) ** 2

# load a previously created study

# study.optimize(
#     objective, 
#     n_trials=100  # the number of values the study will try
# )

if __name__ == '__main__':
    # conn = sqlite3.connect(db_path)
    # conn.close()
    # study_name = "example-study"  # Unique identifier of the study.
    # storage_name = "sqlite:///{}.db".format(study_name)
    study = optuna.create_study(study_name='db', storage=str(db_path))

    # study = load_study(
    # study_name='db', 
    # storage=storage_name,
    # )

# import subprocess
 
# def create_study(study_name, dataset, trial_job_cnt, trials_per_job, api_key, storage, sampler):
    
#     study = optuna.create_study(
#         study_name=study_name,
#         storage=storage, 
#         sampler=sampler, 
#         direction="minimize"
#     )
    
#     # Tell Optuna to start with our default config settings
#     study.enqueue_trial(
#         {
#         "vocab_size": config['models'][0]['synthetics']['params']['vocab_size'],
#         "reset_states": config['models'][0]['synthetics']['params']['reset_states'],
#         "rnn_units": config['models'][0]['synthetics']['params']['rnn_units'],
#         "learning_rate": config['models'][0]['synthetics']['params']['learning_rate'],
#         "gen_temp": config['models'][0]['synthetics']['params']['gen_temp'],
#         "dropout_rate": config['models'][0]['synthetics']['params']['dropout_rate'],
#         }
#     )
    
#     # We will run a total of "trial_cnt" trials with "trial_job_cnt" number of processes running in parallel
    
#     trial_cnt = str(trials_per_job)
#     for i in range(trial_job_cnt):
#         mytrial = subprocess.Popen(["python", "Optuna_Trials.py", study_name, trial_cnt, dataset, api_key, storage])
    
#     return study

# if __name__ == "__main__":


# ### SWEEP ###





# if __name__ == '__main__':
#     args = get_sys_arg()




# $ mysql -u root -e "CREATE DATABASE IF NOT EXISTS example"
# $ optuna create-study --study-name "distributed-example" --storage "mysql://root@localhost/example"
# [I 2020-07-21 13:43:39,642] A new study created with name: distributed-example
''' sql lite
NULL – Includes a NULL value
INTEGER – Includes an integer
REAL – Includes a floating point (decimal) value
TEXT. – Includes text
BLOB. – Includes a binary large object that is stored exactly as input


'''

import sqlite3
# conn = sqlite3.connect('orders.db')
connection = sqlite3.connect("./test/db.db")  # needs dir to exist

import optuna


database_url = "mysql://root@localhost/example"
hypam_opt_alg = ''  # https://optuna.readthedocs.io/en/stable/reference/samplers/index.html
hypam_opt_stop_alg = ''

optuna.create_study(
    storage=database_url,
    sampler=optuna.TPESampler,
    pruner=optuna.MedianPruner,
    study_name=exp_name,
    direction='minimize',
    load_if_exists=True   
    )
#  optuna create-study --study-name "distributed-example" --storage 




def objective(trial):
    x = trial.suggest_float("x", -10, 10)
    return (x - 2) ** 2

# https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html#which-sampler-and-pruner-should-be-used



if __name__ == "__main__":
    study = optuna.load_study(
        study_name="distributed-example", storage="mysql://root@localhost/example"
    )

    study.optimize(objective, n_trials=100)