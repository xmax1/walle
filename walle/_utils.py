import pickle as pk
from pathlib import Path
from typing import Any



# CogSys tasks
@task
def gpustat(c):
    """Run gpustat on all hosts.

    Example:
        $ fab gpustat
    """
    ThreadingGroup(*HOSTS, user=USER).run("gpustat")


@task
def screenls(c, host):
    """Run screen -ls on remote host.

    Example:
        $ fab screenls [host]
    """
    host = f"{host}.compute.dtu.dk"
    assert host in HOSTS, f"{host} not in list of known hosts."
    remote = Connection(host, user=USER)
    remote.run(f"screen -ls")


@task
def uptime(c, host):
    """Run uptime on remote host.

    Example:
        $ fab uptime [host]
    """
    host = f"{host}.compute.dtu.dk"
    assert host in HOSTS, f"{host} not in list of known hosts."
    remote = Connection(host, user=USER)
    remote.run(f"uptime")


@task
def run(c, host, device, script):
    """Run script on remote host.

    Example:
        $ fab run [host] [GPU index] "scripts/runner.py --target=U0"
    """
    host = f"{host}.compute.dtu.dk"
    assert host in HOSTS, f"{host} not in list of known hosts."
    assert device.isdigit(), "Device should be an integer."
    assert "--output_dir" not in script, "--output_dir is set automatically."
    commit_time_id = c.run("git show -s --format=%cI-%h HEAD", hide=True).stdout.strip()
    commit_id = commit_time_id.split("-")[-1]
    timestamp = datetime.now().isoformat()
    output_path = Path(f"runs/{timestamp}/")
    gitdetails_path = output_path / "gitdetails.txt"
    screenlog_path = output_path / "screenlog"
    screenrc_path = output_path / "screenrc"

    print(f"Process timestamp: {timestamp}")

    # Prepare commands
    # Source and activate python virtual environment
    env_cmds = f"""
    source /opt/miniconda3/bin/activate
    conda activate {CONDA_ENV}
    """
    # Run script in detached screen process
    cmd = f"screen -c {screenrc_path} -dmSL {timestamp} bash -c "
    cmd += f"'CUDA_VISIBLE_DEVICES={device} "
    cmd += f"python -u {script} --output_dir={output_path}'"
    # cmd += "python -c \"import torch; print(torch.cuda.is_available())\"'"

    # Run commands on remote host
    remote = Connection(host, user=USER)
    with remote.cd(REPO_PATH):
        # Checkout current commit on remote
        remote.run(f"git fetch && git checkout {commit_id}")
        # Create output directory
        if remote.run(f"test -d {output_path}", warn=True).failed:
            remote.run(f"mkdir -p {output_path}")
        # Write git details to file
        remote.run(f"echo {commit_time_id} > {gitdetails_path}")
        # Create screenrc config file
        remote.run(f"echo 'logfile {screenlog_path}' > {screenrc_path}")
        # Activate environment and run command
        with remote.prefix(chain(env_cmds)):
            remote.run("pip install --quiet -r requirements.txt")
            remote.run(cmd)
        # Tail screen log
        remote.run(f"tail -f {screenlog_path}")


@task
def tail(c, host, timestamp, n=10):
    """Tail screen log on remote host.

    Example:
        $ fab tail [host] [timestamp]
    """
    host = f"{host}.compute.dtu.dk"
    assert host in HOSTS, f"{host} not in list of known hosts."
    screenlog_path = Path(f"runs/{timestamp}/screenlog")
    remote = Connection(host, user=USER)
    with remote.cd(REPO_PATH):
        remote.run(f"tail -n {n} -f {screenlog_path}")


@task
def copy(c, host, timestamp):
    """Copy output folder from remote to local runs directory.

    Example:
        $ fab copy [host] [timestamp]
    """
    host = f"{host}.compute.dtu.dk"
    assert host in HOSTS, f"{host} not in list of known hosts."
    c.run(f"scp -r {host}:{REPO_PATH}/runs/{timestamp}/ runs/{timestamp}/")



def save_pk(x: Any, path: Path):
    with open(path, 'wb') as f:
        pk.dump(x, f)

def load_pk(path: str | Path):
    with open(path, 'rb') as f:
        x = pk.load(f)
    return x