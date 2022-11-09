import subprocess
from time import sleep
from itertools import product

''' NVIDIA-SMI
# List gpus available
nvidia-smi -L

# Get more info
nvidia-smi -q
'''




def count_device():
    # TODO this
    return 1

### BONEZONE ### 

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