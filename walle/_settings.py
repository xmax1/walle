"""Developer settings

Copy these settings to a new file called 'settings.py'.
"""
# Settings for running scripts on a remote host

# DTU username
USER = "pbjo"

# List of hostnames
HOSTS = """
mnemosyne.compute.dtu.dk
theia.compute.dtu.dk
phoebe.compute.dtu.dk
themis.compute.dtu.dk
oceanus.compute.dtu.dk
hyperion.compute.dtu.dk
coeus.compute.dtu.dk
cronus.compute.dtu.dk
crius.compute.dtu.dk
iapetus.compute.dtu.dk
""".strip().split()

# Path to git repository on remote
REPO_PATH = "./graphnn/"

# The cuda module that will be loaded on the remote
CUDA_MODULE = "cuda10.2-cudnn7.6"

# The conda envronment that will be activated on the remote
CONDA_ENV = "nenv"

# Niflheim settings
NIFLHEIM_VIRTUAL_ENV = "~/graphnn_py39env"

NIFLHEIM_REPO_SCRATCH = "~/graphnn_revisions"
NIFLHEIM_PYTHON_MODULE = "Python/3.9.5-GCCcore-10.3.0"
NIFLHEIM_LOGIN_HOST = "slid.fysik.dtu.dk"

NIFLHEIM_SCRIPT_PREAMBLE = f"""#!/bin/bash -ex
#SBATCH --mail-type=END,FAIL
#SBATCH --partition=sm3090
#SBATCH -N 1      # Minimum of 1 node
#SBATCH -n 8     # 10 MPI processes per node
#SBATCH --time=7-00:00:00
#SBATCH --gres=gpu:RTX3090:1

module load {NIFLHEIM_PYTHON_MODULE}
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
source {NIFLHEIM_VIRTUAL_ENV}/bin/activate
python -m threadpoolctl -i torch numpy scipy
"""

