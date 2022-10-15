import os.path

import click
import re
from Modules.FileHandle import FileHandler, list_all_files


@click.group()
def cli():
    pass


@cli.command()
@click.argument('file_paths',
                nargs=-1, )
@click.option('-n', '--name', '--archive-name',
              type=click.STRING,
              prompt="Enter archive name")
def encode(file_paths: str, name):
    """Encodes files from file path."""

    #if not file_paths:
    #    file_paths = click.prompt('Enter at least one file path')

    print(file_paths)

    fHandler = FileHandler()
    fHandler.loadConfig('header_config.json', 'DefaultHeader')
    fHandler.encodeFile(file_paths, outputName=name)


@cli.command()
@click.argument(
    'file_paths',
    nargs=-1,
    type=click.Path(exists=True))
@click.option(
    '-h', '--header',
    type=click.Choice(['Default', 'First', 'Second'], case_sensitive=False),
    default='Default')
def decode(file_paths, header):
    """Decodes files from file path."""

    fHandler = FileHandler()

    headers = {'Default': 'DefaultHeader',
               'First': 'FirstHeader',
               'Second': 'SecondHeader'
               }

    head = headers[header]

    fHandler.loadConfig('header_config.json', head)
    for file in file_paths:
        fHandler.decodeFile(file, encoding='utf-8')
