
- spec file for identical environment
conda list --explicit > spec-file.txt

- NVCC 
terminal: nvcc --version

nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2021 NVIDIA Corporation
Built on Sun_Feb_14_21:12:58_PST_2021
Cuda compilation tools, release 11.2, V11.2.152
Build cuda_11.2.r11.2/compiler.29618528_0

terminal: whereis nvcc
nvcc: /opt/cuda/cuda-11.2/bin/nvcc.profile /opt/cuda/cuda-11.2/bin/nvcc

# Issues
- JAX can't see GPU
    - https://github.com/google/jax/issues/5231
    - find CUDA / cuDNN version
- Some functions in another place
`
Note that some GPU functionality expects the CUDA installation to be at /usr/local/cuda-X.X, where X.X should be replaced with the CUDA version number (e.g. cuda-10.2). If CUDA is installed elsewhere on your system, you can either create a symlink:

sudo ln -s /path/to/cuda /usr/local/cuda-X.X

# can't create symbolic link - how does it know where to get cuda?
ln -s /opt/cuda/cudnn-11.4 /usr/local/cuda-11.4

Or set the following environment variable before importing JAX:

XLA_FLAGS=--xla_gpu_cuda_data_dir=/path/to/cuda
`

# - remove tensorflow gpu access
# - run svol test
# - tensor rt libraries
# - add gcc 


- EXCEEDED QUOTA
conda clean --all
pip cache purge

# BUGS
- None of the algorithms provided by cuDNN heuristics worked; trying fallback algorithms
