import sys
import subprocess
from contextlib import redirect_stdout
from ast import literal_eval
import io
from stat import S_ISDIR, S_ISREG
import wandb

import paramiko
from simple_slurm import Slurm
from pathlib import Path

from .bureaucrat import mkdir, gen_alphanum
from .idiomatic import zip_in_n_chunks, flat_list
from cfg.cfg import Pyfig

### GPUS ###
def get_env_var(k: str):
    return run_cmd(f'echo ${k}') 

def set_env_var(k: str):
    run_cmd(f'export ${k}')
    return 

def count_gpu() -> int:
    # output = run_cmd('echo $CUDA_VISIBLE_DEVICES', cwd='.')
    import os
    cvd = os.environ.get('CUDA_VISIBLE_DEVICES')
    cvd = None if cvd == '' else cvd
    return len(cvd.split(',')) if not cvd is None else 0 

def get_gpu_utilisation() -> dict:
    """ Find all GPUs and their total memory """
    output = run_cmd('nvidia-smi --query-gpu=index,memory.total --format=csv')
    total_memory = dict(row.replace(',', ' ').split()[:2] for row in output.strip().split('\n')[1:])
    return {gpu_id: {'used': 0, 'used_by_others': 0, 'total': int(total)} for gpu_id, total in total_memory.items()}

def get_free_gpu_id() -> int | None:
    ut_all = get_gpu_utilisation()
    for idx, ut in enumerate(ut_all):
        if ut < 100:
            return idx
    return None

### SERVER CMD ###
def open_ssh(
    user    : str  = None,
    server  : str  = None,
    sftp    : bool = False
):
    """ 
    EDU SFTP SSH File Transfer Protocol """

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # if not known host
    client.connect(hostname=server, username=user) # ,password = ’mypassword’)
    if sftp:
        return client.open_sftp()
    else:
        return client

### LOCAL CMD ###
def run_cmd(cmd: str, cwd: str | Path, input_req: str = None) -> str:
    process = subprocess.run([c.strip() for c in cmd.split(' ')], cwd=cwd, input=input_req, capture_output=True)   # check = True error raise on fail
    print('STDERR: \n', process.stderr)
    return process.stdout

### GIT ###
def git_commit(
    project_dir : str | Path,
    remote      : str = 'origin',
    branch      : str = 'main',
    msg         : str = ''
) -> str:
    """ 
    NB Don't need to include walle functionality because assuming walle stable 
    EDU The subprocess module allows us to spawn processes, connect to their
    input/output/error pipes, and obtain their return codes """
    run_cmd('git add .', cwd=project_dir)
    run_cmd(f'git commit -m "{msg}"', cwd=project_dir)
    run_cmd(f'git push {remote} {branch}', cwd=project_dir)
    return git_commit_id(cwd=project_dir)

def git_commit_id(cwd: str | Path) -> str:
    stdout = run_cmd('git log -1', cwd=cwd).decode('utf-8')  
    commit_id = stdout.replace('\n', ' ').split(' ')[1]
    return commit_id

def git_pull(project_dir: str | Path, remote: str = 'origin', branch: str = 'main') -> str:  
    stdout = run_cmd(f'git pull {remote} {branch}', cwd=project_dir)
    return stdout

def git_connect_repo(
    target: str|Path,
    remote: str|Path,
    branch: str     = 'main',
    msg:    str     = 'First WALLE commit, congratulations',
):
    run_cmd('git init', cwd=target)
    run_cmd('git add .', cwd=target)
    run_cmd('git add .', cwd=target)
    run_cmd(f'git commit -m {msg}', cwd=target)
    run_cmd(f'git branch -M {branch}', cwd=target)
    if remote is not None:
        run_cmd(f'git remote add origin {remote}', cwd=target)
        run_cmd(f'git push -u {remote} {branch}', cwd=target)    
        print(f'New project repo initialised and pushed to {remote}')
    else:
        print('repo initialised BUT !! not pushed. Add remote next time.')

tmp = mkdir(Path('./tmp/out'))
mv_cmd = f'mv {tmp}/o-$SLURM_JOB_ID.out {tmp}/e-$SLURM_JOB_ID.err $out_dir'

### SUBMISSION ###
def submit_sweep(
    c           : Pyfig,
    msg         : str = '',
):  
    """ commits local changes, pulls changes to cluster, runs run_name
    NB  server cmd executed from server_project_dir
    """
    stdout = run_cmd('git add .', cwd=c.project_dir)
    stdout = run_cmd(f'git commit -m "{msg}"', cwd=c.project_dir)
    stdout = run_cmd(f'git push {c.git_remote} {c.git_branch}', cwd=c.project_dir)

    with open_ssh(c.user, c.server, sftp=False) as client:
        stdin, stdout, stderr = client.exec_command(f'cd {c.server_project_dir}')
        stdin, stdout, stderr = client.exec_command(f'git pull {c.git_remote} {c.git_branch}')
        stdin, stdout, stderr = client.exec_command(f'python {c.run_path} --run sweep_lord')

    return None

def gen_cmd(c: Pyfig = None):
    if c:
        cmd = f'python -u {c.run_path}'   
        for k, v in c.dict.items():
            cmd += f' --{k} {str(v)}'
    else:
        pass # TODO the case where they don't use a config
    return cmd

def submit_sweep_agent_all(c: Pyfig):
    c.sweep_id = wandb.sweep(
            env     = f'conda activate {c.env};',
            sweep   = c.sweep, 
            program = c.run_path,
            project = c.project,
            name    = c.exp_name,
            run_cap = c.n_sweep
        )
    for _s in range(c.n_sweep):
        c.submit_slurm(agent=True, exp_id=True)
    exit('Run sweep')

def run_single_slurm(
    exp_path    : Path,
    slurm_cfg   : str,
    sbatch_cfg  : str,
    cmd         : str
) -> None:
    """ 
    EDU -u in python call unbuffers stdout 
    NB  creates out_dir and moves err and out files after run 
    EDU slurm config details https://slurm.schedmd.com/pdfs/summary.pdf """   

    # TODO slurm = Slurm(array=range(3, 12), job_name='name')
    # TODO slurm.set_dependency(dict(after=65541, afterok=34987))
    slurm = Slurm(
        output =    tmp / 'o-%j.out',
        error  =    tmp / 'e-%j.err',
        **slurm_cfg,
    )

    print('RUNNING: \n ', cmd)
    slurm.sbatch(
        sbatch_cfg + 
        f'out_dir={(mkdir(exp_path)/"out")} \n \
        {cmd} | tee $out_dir/py.out \n \
        {mv_cmd} \n \
        date "+%B %V %T.%3N" '
    )
    return None

booleans = ['True', 'true', 't', 'False', 'false', 'f']

def get_sys_arg() -> dict:
    """ collects arguments from sys and parses 
    NB  only --flag arg structure works """
    arg = ' '.join(sys.argv[1:])
    if len(arg) == 0:
        return {}

    # allow user to input args like -arg and --arg
    arg_standard_dash = arg.replace('--', '-')  
    
    # [1:] because the zeroth split gives an empty element ''
    arg_split = arg_standard_dash.split('-')[1:]  
    
    # split by the first whitespace, avoid split lists/tuples
    arg_split_by_first_ws = flat_list([x.split(' ', maxsplit=1) for x in arg_split])  
    
    # remove all the whitespace left and right, all that should be left is whitespace in lists and tuples
    arg = [x.rstrip(' ').lstrip(' ').replace(' ', ',') for x in arg_split_by_first_ws]  

    out_arg = {}
    for k, v in {k:v for k,v in zip_in_n_chunks(arg, 2)}.items():
        if v in booleans:  # ADDING REDUNDANCY: For if the boolean argument is mispelt
            out_arg[k] = ('t' in v) or ('T' in v)
        else:
            try:
                out_arg[k] = literal_eval(v)
            except:
                out_arg[k] = v  # strings don't work in literal eval mk YYYY
    return out_arg

""" SLURM ARGS
JOB_ARRAY_MASTER_ID	%A	job array's master job allocation number
JOB_ARRAY_ID	%a	job array id (index) number
JOB_ID_STEP_ID	%J	jobid.stepid of the running job. (e.g. "128.0")
JOB_ID	%j	jobid of the running job
HOSTNAME	%N	short hostname. this will create a separate io file per node
NODE_IDENTIFIER	%n	node identifier relative to current job (e.g. "0" is the first node of the running job) this will create a separate io file per node
STEP_ID	%s	stepid of the running job
TASK_IDENTIFIER	%t	task identifier (rank) relative to current job. this will create a separate io file per task
USER_NAME	%u	user name
JOB_NAME	%x	job name
PERCENTAGE	%%	the character "%"
DO_NOT_PROCESS	\\	do not process any of the replacement symbols
"""

def test():
    import os
    # os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2'
    print(count_gpu())
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    print(count_gpu())
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    print(count_gpu())

    # python submit.py --wstring string --wfloat 0.1 --wint 1 --wbool true --wlist [1,2,3]  # list constrained to no spaces
    arg = get_sys_arg()
    for k, v in arg.items():
        print(k, v, type(v))

    
if __name__ == '__main__':
    ''' NOTES
    - Assumes running a conda env. To run something else, remove conda line from slurm.sbatch
    - Other sbatch defaults can be changed in the Slurm() class, you can use all these pieces to make functions for what you need
    - run_dir is where the results go 
    - exp_name is another tag so sweeps can go together (ie keep run_dir the same but change exp_name)
    '''
    test()
    
    


#     exp_kwargs = {
#         # experiment hyperparams go here and are passed in as cmd line args
#     }
    
#     run_single_slurm(
#         execution_file  = 'demo.py',  # what we are running
#         submission_name = 'hp',       # slurm name (not id)
#         env             = 'dex',     # conda environment 
#         time_h          = 24,  
#         run_dir         = '../experiments/remote_demo',
#         exp_name        = 'flowers',        
#         **exp_kwargs
#         )



# if __name__ == '__main__':
#     pass


# def create_typed_arg(arg: dict) -> dict:
#     """ converts command line arguments to types
#     NB  works with [bytes, numbers, tuples, lists, dicts, sets, booleans, None, Ellipsis]
#     NB  crashes on string, so an exception is called (TODO: why)
#     """
#     arg_typed = {}
#     for k, v in arg.items():
        
#         if v in booleans:                           # REDUNDANCY: The boolean argument isn't written correct
#             arg_typed[k] = ('t' in v) or ('T' in v)
        
#         else:
#             try:
#                 arg_typed[k] = literal_eval(v)
#             except Exception as e:
#                 arg_typed[k] = str(v)

#     return arg_typed


# def collect_sysarg() -> dict:
#     """
#     NB  assumes arguments to any experiment are --arg_name value
#     EDU .replace default is replace all arg0 with arg1 
#     EDU .split(seperator=None, maxsplit=1) https://stackoverflow.com/questions/30636248/split-a-string-only-by-first-space-in-python""" 
#     if len(sys.argv) == 1:
#         return {}
#     else:
#         arg = ' '.join(sys.argv[1:])
#         arg_standard_dash = arg.replace('--', '-')  # allow user to input args like -arg and --arg
#         arg_split = arg_standard_dash.split('-')[1:]  # [1:] because the zeroth split gives an empty element ''
#         arg_split_by_first_ws = [x.split(separator=None, maxsplit=1) for x in arg_split]  # split by the first whitespace, avoid split lists/tuples
#         arg_clean = [x.replace(' ', '') for x in arg_split_by_first_ws]  # remove all the whitespace left
#         return {k:v for k,v in zip_in_n_chunks(arg_clean, 2)}
    



