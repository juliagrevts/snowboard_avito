from argparse import ArgumentParser
from app import create_app
from parsers.avito_parser import get_snowboard_pages_links, save_all_snowboards


parser = ArgumentParser(
    prog='Parser launcher',
    description='The program launchs either parsing links on snowboards (on Safari webdriver)'
    'and writing them to a file, or parsing snowboard elements from snowboards links '
    'and saving snowboards to a database.'
)

parser.add_argument(
    'command',
    choices=['get_snowboards_links', 'get_snowboards'],
    help='provide a command you want to execute from two options'
)
parser.add_argument(
    '-u', '--url',
    help='if command==get_snowboards_links this option allows '
    'to provide a url (put it in quotes) with snowboards links you want to parse'
)
parser.add_argument(
    '-mp', '--max_pages',
    type=int, help=' if command==get_snowboards_links this option allows '
    'to provide a number of website pages with links to parse links'
)
parser.add_argument(
    '-f', '--filename',
    help='if command==get_snowboards_links'
    'provide a filename in which the snowboards links will be written '
    'or from which they will be retrieved to parse snowboards if command==get_snowboards'
)

args = parser.parse_args()
args = vars(args)

if args['command'] == 'get_snowboards_links':
    del args['command']
    get_snowboard_pages_links(**args)
if args['command'] == 'get_snowboards':
    app = create_app()
    with app.app_context():
        save_all_snowboards(args['filename'])
