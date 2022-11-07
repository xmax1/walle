

import sys
import os
from pathlib import Path
from bureaucrat import mkdir, gen_alphanum

this_file = Path(__file__).parent
print(f'wlaunch in {this_file}')

args = sys.argv
path = Path(sys.argv[1])
remote = None
if len(args) == 3:
    remote = sys.argv[2]

print('MAKING NEW PROJECT FOLDER, FLY FREE JEDI')
code_path = path / path.name
configs_path = path / 'configs'
experiments_path = path / 'experiments'

mkdir(path)
mkdir(experiments_path)
mkdir(configs_path)
mkdir(code_path)

print('COPYING USEFUL THINGS...')

# ROOT
os.system(f'cp {str("../.gitignore")}  {str(path / ".gitignore")}')
os.system(f'cp {str("../.demo_instruction.md")}  {str(path / "demo_instruction.md")}')

os.system(f'cp -r {str(this_file/ "notes")}  {str(path / "notes")}')
os.system(f'cp {str(this_file/ "templates/user.py")}  {str(path / "user.py")}')

# CONFIGS
os.system(f'cp {str(this_file/ "templates/cfg.yaml")}  {str(configs_path / "cfg.yaml")}')
os.system(f'cp {str(this_file/ "templates/sweep_cfg.yaml")}  {str(configs_path / "sweep_cfg.yaml")}')

# CODE
os.system(f'cp {str(this_file/ "templates/paths.py")}  {str(code_path / "paths.py")}')
os.system(f'cp {str(this_file/ "templates/algs.py")}  {str(code_path / "algs.py")}')
os.system(f'cp {str(this_file/ "templates/run.py")}  {str(code_path / "run.py")}')
os.system(f'touch {str(code_path /"__init__.py")}')

# ANALYSIS
exp_path = experiments_path / 'exp_name'
demo_exp_path = exp_path / f"sweep_tag_eg_{gen_alphanum(7)}"


mkdir(demo_exp_path / 'all_code_from_this_specific_run')
mkdir(demo_exp_path / 'models_and_other_dumped_artifacts')
mkdir(demo_exp_path / 'wandb_files')

os.system(f'cp {str(this_file/ "templates/analysis.ipynb")}  {str(exp_path / "analysis.ipynb")}')
os.system(f'touch {str(demo_exp_path/"err.out")}')
os.system(f'touch {str(demo_exp_path/"out.out")}')
os.system(f'touch {str(demo_exp_path/"py.out")}')
os.system(f'touch {str(demo_exp_path/"cfg.yaml")}')
os.system(f'touch {str(demo_exp_path/"optuna.db")}')

print('PUT WALLE IN THE PYTHONPATH')

print('MAKING GIT REPO...')
def make_git_repo(remote=None):
    os.chdir(path)
    os.system('git init')
    os.system('git add .')
    os.system('git commit -m "first commit"')
    os.system('git branch -M main')
    if remote is not None:
        os.system(f'git remote add origin {remote}')
        os.system('git push -u origin main')
        print('repo initialised and pushed')
    else:
        print('repo initialised and not pushed, add remote next time')

make_git_repo(remote=remote)