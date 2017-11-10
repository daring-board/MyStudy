import argparse

def _launch():
    parser = argparse.ArgumentParser(
        prog = 'python -m pipline',
        description = __doc__
    )
    parser.add_argument(
        '-k',
        '--keep-going',
        action = 'store_true',
        default = False
    )
    parser.add_argument('filename')
    args = parser.parse_args()
    """
    コマンドライン引数名：keep_goingに対して、
    値が入っていれば、args.keep_goingがTrue。デフォルトはFalse。
    入っている値は、args.filenameに格納される。
    ex. python -m pipline -k aaa.txt
    """
    print(args.keep_going)
    print(args.filename)

if __name__=='__main__':
    _launch()
