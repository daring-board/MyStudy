import argparse
parser = argparse.AguremntParser(
    prog = 'python -m apdemo'
    description = 'Hello world'
)
parser.add_argument('-p', '--print', action='store_ture', default=False)
parser.add_argument('name', nargs='+')
args = parser.parser_args()
