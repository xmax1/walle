from pathlib import Path
from walle.pyfig import pyfig

cfg_path = Path('.').parent() / 'cfg' / 'cfg.py'
    # mkdir(r'C:\Users\max\OneDrive\sisy\walle\exp')
print(cfg_path.absolute())
c = pyfig(cfg_path=Path(cfg_path).absolute())