from contextlib import redirect_stdout
from stat import S_ISDIR, S_ISREG
import shutil
import os
import io

import paramiko
from pathlib import Path

from .bureaucrat import mkdir

try:
    from user import username, server
except:
    print('Couldn\'t import username and server')
    username, server = '', ''


def listdir_r(sftp, remotedir):
    for entry in sftp.listdir_attr(remotedir):
        remotepath = remotedir + "/" + entry.filename
        mode = entry.st_mode
        if S_ISDIR(mode):
            listdir_r(sftp, remotepath)
        elif S_ISREG(mode):
            if not ((remotepath[-1] == '.') or (remotepath[-2:] == '..') or (remotepath == '')):
                print(remotepath)


def fetch(
    username=username,
    server=server,
    server_dir=None,
    target_dir=None,            # the directory it is going in
    avoid: list = None,
    match: list = None,
    in_folders: list = None,
    print_paths: bool = False,
    pull: bool = True
): 
    ssh_client=paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # if not known host
    ssh_client.connect(hostname=server, username=username) # ,password = ’mypassword’)
    sftp=ssh_client.open_sftp()

    f = io.StringIO()
    with redirect_stdout(f):
        listdir_r(sftp, server_dir)
    remote_paths = f.getvalue().split('\n')
    remote_paths = [Path(f.strip('\n')) for f in remote_paths if f not in ['', '.', '..', '\n']]

    if match is not None:
        remote_paths = [f for f in remote_paths if any([f.match(f'*{x}*') for x in match])]

    if avoid is not None:
        remote_paths = [f for f in remote_paths if not any([x in str(f) for x in avoid])]
    
    target_dir = Path(target_dir)

    print(f'{len(remote_paths)} files found')
    for f in remote_paths:
        local_path = target_dir / Path(f).relative_to(server_dir)
        
        if pull:
            print(f'Making local path {local_path}')
            mkdir(local_path)
            try:
                if print_paths:
                    print('Pulling: ')
                    print(f'Server: {str(f)}')
                    print(f'Local: {str(local_path)}')
                sftp.get(f.as_posix(), str(local_path))
                
            except Exception as e:
                print(e)

    sftp.close()


def fetch_from_folders(folders: list, rss: list, fnames: list, server: str, save_dir: str = 'walkers'):
    if Path(save_dir).is_dir():
        input("Dir exists, press Enter to continue and erase")
        shutil.rmtree(save_dir)
    path = Path(save_dir)
    path.mkdir()
    for rs, folder in zip(rss, folders):
        for fname in fnames:
            fpath = folder / fname
            print(f'fetching {fpath.parent}')
            os.system(f'scp -r {server}:{fpath.as_posix()} {save_dir}/rs{rs}_{fpath.name}')
            



if __name__ == '__main__':
    root = Path('/home/energy/amawi/projects/nn_ansatz/src/experiments/HEG/final1001/14el/baseline/kfac_1lr-3_1d-4_1nc-4_m2048_el14_s128_p32_l3_det1')
    folders = [
        ['run41035', 10],
        ['run301115', 100],
        ['run341241', 50],
        ['run659627', 1],
        ['run848588',  5],
        ['run874318', 20],
        ['run924186', 2]
    ]
    rss = [f[1] for f in folders]
    folders = [root / f[0] for f in folders]
    fnames = ['eq_walkers_i100000.pk']

    fetch_from_folders(folders, rss, fnames, server='amawi@svol.fysik.dtu.dk')

    exit()

    fetch(paths, server='amawi@svol.fysik.dtu.dk')

    def load_pk(path):
        with open(path, 'rb') as f:
            x = pk.load(f)
        return x

    experiments = [
        'one_body',
        'pair_corr',
        'mom_dist'
    ]

    dimension_tags = [
        '',
        '_d3',
    ]

    data_folder = 'fetched_files'
    rss = [1, 2, 5, 10, 20, 50, 100]

    data = {}
    for dim in dimension_tags:
        for rs in rss:
            for exp in experiments:
                filename = f'exp_stats_{exp}{dim}_rs{rs}.pk'
                filepath = f'./{data_folder}/{filename}'
                d = load_pk(filepath)
                data[f'{exp}{dim}_rs{rs}'] = d
                print(d.keys())
            break

    
    



