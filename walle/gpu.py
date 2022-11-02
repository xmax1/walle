import subprocess
from time import sleep
from itertools import product

''' NVIDIA-SMI
# List gpus available
nvidia-smi -L

# Get more info
nvidia-smi -q

'''

def get_gpu_utilisation():
    # Find all GPUs and their total memory
    command = ["nvidia-smi", "--query-gpu=index,memory.total", "--format=csv"]
    output = subprocess.check_output(command).decode("utf-8")
    total_memory = dict(row.replace(",", " ").split()[:2]
        for row in output.strip().split("\n")[1:])

    # Store GPU usage information for each GPU
    gpu_usage = {gpu_id: {"used": 0, "used_by_others": 0, "total": int(total)}
        for gpu_id, total in total_memory.items()}

    return gpu_usage


def get_free_gpu_id():
    ut_all = get_gpu_utilisation()
    for idx, ut in enumerate(ut_all):
        if ut < 100:
            return idx
    return None




# BONEZONE

def get_gpu_utilisation_dep():
    ''' Works on gpustat on compute cluster
    '''
    out = subprocess.check_output(['gpustat'])
    out = out.decode('ASCII')
    out = out.split('\n')
    out = out[1:-1]
    out = [o.split('|') for o in out]
    out = [o[2] for o in out]
    out = [o.replace(' ', '') for o in out]
    out = [o.split('/')[0] for o in out]
    out = [int(o) for o in out]
    return out