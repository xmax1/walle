





# YAML

class Array(yaml.YAMLObject):
    '''
    definition of a yaml descriptor
    node: all the characters indented after the name
    decomposes to a sequence and can iterate over the sequence by its value
    
    from yaml import ScalarNode
    '''
    yaml_tag = u'!jax_or_numpy_arr'
    
    @classmethod
    def from_yaml(cls, constructor, node):
        
        array = []
        for sub_node in node.value:
            print(sub_node.tag)
            if 'seq' in sub_node.tag:
                array.append([float(v.value) if 'float' in v.tag else int(v.value) for v in sub_node.value])
            else:
                array.append(float(sub_node.value) if 'float' in sub_node.tag else int(sub_node.value))

        return np.array(array)


def load_yaml(path: str) -> dict:
    with open(path, 'r') as f:
        args = yaml.load(f, Loader=yaml.FullLoader)
    return args


def write_dict(d: dict, f: TextIO):
    for k, v in d.items():
        v = array_to_lists(v)

        if type(v) in [str, int, float]:
            f.writelines(f'{k}: !!{type(v).__name__} {v} \n')
        
        if isinstance(v, list):
            f.writelines('{}: !!seq {} \n'.format(k, v if not isinstance(v[0], list) else ''))
            if isinstance(v[0], list):
                for l in v: 
                    f.writelines(f'  - !!seq {l} \n')

        if isinstance(v, dict):
            f.writelines(f'{k}: !!map \n')
            write_dict(v, f)

        if isinstance(v, Path):
            f.writelines(f'{k}: !!str {v.as_posix()} \n')
    return 


def save_dict_as_yaml(d: dict, path: str):
    """ like this to allow recursion """
    with open(path, 'w') as f:
        write_dict(d, f)


# numpy 


# pickle

def save_pk(x: Any, path: Path):
    
    if isinstance(x, dict):
        x = {k: to_numpy(v) for k, v in x.items()}
    else:
        x = to_numpy(x)

    with open(path, 'wb') as f:
        pk.dump(x, f)


def load_pk(path: str) -> dict | np.ndarray:
    with open(path, 'rb') as f:
        x = pk.load(f)
    return x


def check_content_pk(d: dict | np.ndarray):
    for k, v in d.items():
        print(k, v.shape)


# pandas

def df_to_dict(df: pd.DataFrame, type_filter: list = []) -> dict:
    return {c:np.array(df[c]) for c in df.columns if df[c].dtypes not in type_filter}


# create zip file


def zip_files(path: Path | list[Path], zip_root: Path, name='files.zip'):
    
    if isinstance(path, list):
        pass
    elif path.is_dir():
        path = path.iterdir()
    elif path.is_file():
        path = [path]
    
    print(f'Zipping {len(list(path))} files in {name}')
    with ZipFile(name, 'w') as f:
        for p in path:
            arcname = p.relative_to(zip_root)          
            f.write(str(p), arcname=arcname)


def something_remove():
    from pathlib import Path
    from shutil import copytree, copyfile, rmtree
    import shutil

    root = Path('/home/energy/amawi/projects/nn_ansatz/src/experiments/HEG/final1001/14el/baseline/kfac_1lr-3_1d-4_1nc-4_m2048_el14_s128_p32_l3_det1')
    target = Path('/home/energy/amawi/projects/nn_ansatz/src/experiments/PRX_Responses/runs')
    cfg_paths = root.rglob('config*')

    for p in cfg_paths:
        target_dir = (target / p.relative_to(root)).parent

        if not target_dir.exists():
            target_dir.mkdir(parents=True)

        cfg = target_dir / p.name
        if cfg.exists():
            try:
                cfg.unlink()
            except:
                rmtree(cfg)

        copyfile(p, cfg)
        copytree(str(p.parent / 'models'), str(target_dir / 'models'), dirs_exist_ok=True, )


# NAMING

def gen_alphanum(n=7):
    uppers = string.ascii_uppercase
    lowers = string.ascii_lowercase
    numbers = ''.join([str(i) for i in range(10)])
    characters = uppers + lowers + numbers
    name = ''.join([random.choice(characters) for _ in range(n)])
    return name


def gen_datetime() -> str:
    return datetime.now().strftime("%d%b%H%M%S")


def now_tag() -> str:
    return datetime.now().strftime('%M%S')


def date_to_num():
    today = datetime.today()
    tdelta = today - datetime(year=today.year, month=1, day=1) 
    name = f'{str(today.year)[2:]}_{tdelta.days}_{str(tdelta.microseconds)[-4:]}'
    return name

def iterate_folder(folder: Path):
    exist = [int(x.split('-')[1]) for x in folder.iterdir() if '-' in x.name]
    for i in range(100):
        if i in exist:
            break
    folder = add_to_Path(folder, f'-{i}')
    return folder

### TESTING ###

def tests():
    from .idiomatic import flatten_lst_of_lst
    path = Path(r'C:\Users\max\OneDrive\sisy\hwapnet\analysis\PRX_responses\runs')
    match =  ['exp_stats_pair_corr_d3_new', 'exp_stats_one_body_d3', 'exp_stats_mom_dist_3', 'config.pk']
    files = [path.rglob(f'*{m}*') for m in match]
    files = flatten_lst_of_lst(files)
    zip_files(files, name=r'.\runs\results\d3_obs_data.zip', zip_root=path)

    return 


if __name__ == '__main__':

    tests()