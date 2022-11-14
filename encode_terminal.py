import click
from Modules.FileHandle import FileHandler


@click.group()
def cli():
    pass


@cli.command()
@click.argument('file_paths',
                nargs=-1, )
@click.option('-n', '--name', '--archive-name',
              type=click.STRING,
              prompt="Enter archive name")
@click.option('-c', '--compress', '--archive-name',
              type=click.STRING)
def encode(file_paths: str, compress: str, name):
    """Encodes files from file path."""

    if not compress:
        compress = 0
    else:
        compress = compress.split(',')
        compress = tuple([int(i.strip()) for i in compress])

        if len(file_paths) != len(compress) and len(compress) > 1:
            raise ValueError("Count of files and compression methods must be equal")


    fHandler = FileHandler()
    fHandler.loadConfig('header_config.json', 'DefaultHeader')
    fHandler.encodeFile(file_paths, outputName=name, compression_alg=compress)


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
