from typing import Any, Callable, Iterable, TextIO

from pathlib import Path

THIS_DIR = Path(__file__).parent

PROJECT_HEAD = Path(__file__).parent
assert PROJECT_HEAD.stem == 'walle', f'{PROJECT_HEAD.stem} change project head in boring utils so it points to walle dir plz'


### TESTING ###

def tests():
    return 

if __name__ == '__main__':

    tests()