import sys
import os
from pathlib import Path
from bureaucrat import mkdir
from shutil import copy, copytree
from submit import git_connect_repo

print(f'wlaunch in {(this_dir := Path(__file__).parent)}')
walle_dir = this_dir.parent

""" SETUP
sys.argv: [this_file_name, project_path, git_remote]
NB  current framework local_project_path == server_project_path but leave variables for potential changes
"""

project_dir = Path(sys.argv[1])
project_name = project_dir.name
git_remote = sys.argv[2] if len(sys.argv) > 2 else None

print('MAKING NEW PROJECT FOLDER, FLY FREE JEDI')
cfg_dir = mkdir(project_dir / 'cfg')
exp_dir = mkdir(project_dir / 'exp')
code_dir = mkdir(project_dir / project_name)
template_dir = Path('./template')

def copy_fd(source: Path, target: Path, names: str|list):
    """
    """
    mkdir(target)

    if isinstance(names, str):
        names = [names]
    
    for name in names:
        source_p = source/name
        target_p = target/name
        if source_p.is_file():
            copy(source_p, target_p)
            print(f'copying file: {source_p} to {target_p}')
        elif source_p.is_dir():
            copytree(source_p, target_p)
            print(f'copying dir: {source_p} to {target_p}')
        elif not source_p.exists():
            print(f'touching file: {target_p}')

copy_fd(this_dir, project_dir, ['template',])
copy_fd(this_dir, exp_dir, ['exp_demo',])
copy_fd(template_dir, project_dir, ['run.py', 'sweep.py', '.gitignore', 'demo_instruction.md', 'sandbox.ipynb'])
copy_fd(template_dir, cfg_dir, ['config.py', '__init__.py'])
copy_fd(template_dir, code_dir, ['analysis.py', '__init__.py',])
copy_fd(template_dir, exp_dir, ['analysis.ipynb', 'exp_structure',])

if not str(walle_dir.absolute()) in sys.path:
    print('WALLE: ', str(walle_dir))
    print('PYTHONPATH: \n ', '\n'.join(sys.path))
    with open(f'{(project_init_path:=project_dir/"__init__.py")}', 'w') as f:
        f.writelines(cmd:=f'sys.path.append({walle_dir})')
    print(f'I wrote  in {project_init_path}, u welcome')

print('MAKING GIT REPO...')
git_connect_repo(project_dir, remote=git_remote, branch='main')