


from zipfile import ZipFile

### ZIP ###
def zip_files(path: Path | list[Path], zip_root: Path, name: str = 'files.zip'):
    
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