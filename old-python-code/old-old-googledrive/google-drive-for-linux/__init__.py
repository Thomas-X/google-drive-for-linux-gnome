import click
import subprocess
from src.utils import check_if_installed, spawn_subprocess
import os
import shutil
from pathlib import Path

home = str(Path.home())
config_directory = os.path.join(home, '.gdfl')

@click.group()
def cli():
    pass

@cli.command()
def one():
    click.echo(' hi world 1')

@cli.command()
def install():
    check_if_installed('ruby', '-v', 'You need to have ruby >= 2.0 installed, use rvm to install ruby.')
    check_if_installed('git', '--version', 'You need to have git installed')
    check_if_installed('bundle', '-v', 'You need to have Bundler, see rvm.')
    if os.path.exists(config_directory):
        shutil.rmtree(config_directory)
    os.mkdir(config_directory)
    os.chdir(config_directory)
    spawn_subprocess(['git', 'clone', 'https://github.com/Thomas-X/drivesync'])
    os.chdir(os.path.join(config_directory, 'drivesync'))
    print(spawn_subprocess(['bundle', 'install']))
    
@cli.command()
def sync():
    


cli.add_command(one)
cli.add_command(install)


# @click.command()
# @click.option('--reset', help='Reset install and authentication.')
# @click.option('--install')
# def gdrive_cli(count, name):
    

if __name__ == '__main__':
    cli()
    # 