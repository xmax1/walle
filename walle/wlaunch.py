import sys
from pathlib import Path
from bureaucrat import mkdir
from shutil import copy, copytree
from submit import git_connect_repo, run_cmd

print(f'wlaunch in {(this_dir := Path(__file__).parent)}')
walle_dir = this_dir.parent
tabs = '\t\t\t'

""" SETUP
sys.argv: [this_file_name, project_path, git_remote]
NB  current framework local_project_path == server_project_path but leave variables for potential changes
"""

print('Hi! Beep boop bap. I hope you\'re having a terrible day.')
print('We\'re going to set some defaults. These will be stored in ~/<project_dir>/_pyfig.py')

with open(project_dir, 'r') as f:
    structure = f.readlines()


print('You can change them any time (in project_dir.py which is a global project config)')
print('Press enter to skip any line, the default (Def:) will be used.')
base_server_project_dir = base_project_dir = Path(input(f'Def: ~/projects {tabs} Where are your projects stored?'))
print('Setting server project dir to the same thing. Go cry about it.')
data_dir = Path(input(f'Def: ~/data {tabs} Where are your data stored?'))
scratch_dir = Path(input(
    f'Def: /scatch/<user> {tabs} What is the path of your user scratch home directory?'
+ f'                    {tabs} Relative paths to data and logs are automatically calculated)...'
))
project_name = Path(input(f'Def: bad_science {tabs} What is the new project called (eg bad_science/sub_project acceptable)?'))
server_project_dir = project_dir = base_project_dir / project_name
git_repo = Path(input(f'Def: nada {tabs} Whats the link to the git repo (go make one)?'))
print(f'auto branch main')
print('Default path structure is this: (change in _pyfig.py to alter future project structures)')
print(f"""
- cfg/<store_pyfigs_here>
- exp/<place_for_data_dump_and_analysis>
- project_name/
\t - notes/<notes_on_everything_from_the_weather_to_bash>
\t - template/<some_templates_that_might_be_useful>
\t - mod/<all_the_model_code_we_have>
\t - wanalysis.py (useful things for analysis)
\t - <your_code_here>
- demo.py (example)
- sandbox.ipynb (example)
- wdocs.md
""")

print('MAKING NEW PROJECT FOLDER, FLY FREE JEDI')
cfg_dir = mkdir(project_dir / 'cfg')
exp_dir = mkdir(project_dir / 'exp')
code_dir = mkdir(project_dir / project_name)

template_dir = Path('./template')

def copy_fd(source: Path, target: Path, names: str|list):
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

copy_fd(this_dir, code_dir, ['template',])
copy_fd(template_dir, project_dir, ['run.py', '.gitignore', 'wdocs.md', 'sandbox.ipynb'])
copy_fd(template_dir, cfg_dir, ['', '__init__.py'])
copy_fd(template_dir, code_dir, ['analysis.py', '__init__.py',])
copy_fd(template_dir, exp_dir, ['analysis.ipynb', 'exp_structure',])

if not str(walle_dir.absolute()) in sys.path:
    print('WALLE: ', str(walle_dir))
    print('PYTHONPATH: \n ', '\n'.join(sys.path))
    with open(f'{(project_init_path:=project_dir/"__init__.py")}', 'w') as f:
        f.writelines(cmd:=f'sys.path.append({walle_dir})')
    print(f'I wrote  in {project_init_path}, u welcome')

print('MAKING GIT REPO...')
git_connect_repo(project_dir, remote=git_repo, branch='main')

# prefix components:
space =  '    '
branch = '│   '
# pointers:
tee =    '├── '
last =   '└── '

def tree(dir_path: Path, prefix: str=''):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """    
    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir(): # extend the prefix and recurse:
            extension = branch if pointer == tee else space 
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix+extension)

for line in tree(project_dir):
    print(line)