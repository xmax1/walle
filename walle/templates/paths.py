"""

NB//
out_dir: intentionally blank, out files go in the run_dir 
plots_dir: plots  # not needed handled in analysis
"""
from pathlib import Path
this_dir = Path(__file__).parent

experiments_dir = str(this_dir / 'experiments')
configs_dir = str(this_dir / 'configs')
