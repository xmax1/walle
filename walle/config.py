import sys
from ast import literal_eval
from idiomatic import zip_in_n_chunks

booleans = ['True', 'true', 't', 'False', 'false', 'f']

def create_types(args: dict) -> dict:
    """ converts command line arguments to types
    
    NB//
    works with [bytes, numbers, tuples, lists, dicts, sets, booleans, None, Ellipsis]
    crashes on string, so an exception is called
    """
    typed_args = {}
    for k, v in args.items():
        
        if v in booleans:  # in case the boolean argument isn't written correct
            v = ('t' in v) or ('T' in v)
        else:
            try:
                v = literal_eval(v)
            except Exception as e:
                v = str(v)

        typed_args[k] = v
    
    return typed_args


def collect_args() -> dict:
    """
    NB//
    assumes arguments to any experiment are --arg_name value
    """ 
    if len(sys.argv) == 1:
        args = {}
    else:
        args = iter(sys.argv[1:])
        args = [a.replace('-', '').replace(' ', '') for a in args]  # replace default is to replace all values
        print(args)
        args = {k:v for k, v in zip_in_n_chunks(args, 2)}
    
    return args


def config():

    var1 = 1
    var2 = 'str'

    cfg = locals()
    return ToClass(cfg)


if __name__ == '__main__':

    # python config.py --wstring string --wfloat 0.1 --wint 1 --wbool true --wlist [1,2,3]  # list constrained to no spaces
    args = collect_args()
    args = create_types(args)

    for k, v in args.items():
        print(k, v, type(v))











''' BONE ZONE 

        # args = iter(sys.argv[1:])
        # args = ' '.join(sys.argv[1:])
        # args = args.split('--')[1:]  # first element is blank, 
        # args = [a.split(' ', 1) for a in args]  # split(chat, max_splits) 
        # args = [x.replace(' ', '') for sub_list in args for x in sub_list]  # make iterable so can iterate in 2s
        # args = {k.replace('-', ''):v for k, v in zip_in_n_chunks(args, 2)}

        # alternate


'''
