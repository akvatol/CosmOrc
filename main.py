import ntpath
import os

import click
import numpy as np
import pandas as pd
from yaml import dump, load
import pysnooper

import utils.gauspar as gauspar
import utils.orpar as orpar
from utils.cospar import Jobs
from utils.reactions import Compound, Reaction

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def condition_pars(cond_str):
    c_l = [float(x) for x in cond_str.split()]
    return np.arange(c_l[0], c_l[1] + c_l[2], c_l[2])


def cosmo_parsing(path, parameters=('Gsolv', 'ln(gamma)', 'Nr')):
    new_path = path.split('.')[0]
    data = Jobs(path).small_df(
        invert=1, columns=parameters).to_csv(f'{new_path}_data.csv')
    settings = Jobs(path ).settings_df().to_csv(
        f'{new_path}_settings.csv')





@click.group()
def cli1():
    pass

#TODO Comments
@cli1.command('generator')
@click.option(
    '-p',
    '--program',
    type=click.Choice(['gaussian', 'orca'], case_sensitive=False),
    default='gaussian',
    prompt='Please choose qm program'
)
@click.option(
    '-i',
    '--iformat',
    default='.log',
    show_default=True,
    prompt='Please, specify *.out file format'
)
@click.argument('path', nargs=1, type=click.Path())
def yaml_generator(path, program, iformat):
    files = []
    # r=root, d=directories, f = file
    for r, d, f in os.walk(path):
        for file in f:
            if iformat in file:
                files.append(os.path.join(r, file))

    data = []
    for f in files:
        name = ntpath.basename(f).split('.')[0]
        path_to_file = f
        data.append({'name':name, 'path_to_file':path_to_file, 'qm_program': program})

    data = {'Compounds':data}

    yaml_file = os.path.join(path, 'file.yaml')

    with open(yaml_file, 'w+') as outfile:
        dump(data, outfile, Dumper=Dumper)


# TODO Fix Natoms bug Orpar and Gauspar
#
@cli1.command('parsing')
@click.argument('files', nargs=-1, type=click.Path())
@click.option(
    '-i',
    '--iformat',
    type=click.Choice(['gaussian', 'orca', 'cosmo'], case_sensitive=False),
    default='gaussian',
    show_default=True,
)
def parsing(files, iformat):
    """
    """
    if iformat == 'g':
        parser = gauspar.file_pars
    elif iformat == 'o':
        parser = orpar.file_pars
    elif iformat == 'c':
        parser = cosmo_parsing 
    with click.progressbar(files) as bar:
        for f in bar:
            new_file_name = os.path.join(
                ntpath.dirname(f),
                ntpath.basename(f).split('.')[0])
            try:
                if iformat in 'go':
                    data = parser(f)
                    data.to_csv(path_or_buf=new_file_name + '.csv')
                elif iformat == 'c':
                    parser(f)
                    # data.to_csv(path_or_buf=new_file_name + '_data_.csv')
                    # settings.to_csv(path_or_buf=new_file_name + '_settings_.csv')
            except Exception as err:
                click.secho(f'Some trouble in {f}', blink=True, bold=True)
                raise err


# Work without COSMO
@cli1.command()
@click.argument('file', nargs=1, type=click.Path())
def reaction(file):
    """
    """
    with open(file, 'r') as f:
        data = load(f, Loader=Loader)

    compounds = [Compound.from_dict(i) for i in data['Compounds']]

    #TODO Fixit
    with click.progressbar(data['Reactions']) as bar:
        for rx in bar:
            p = condition_pars(rx['conditions']['pressure'])
            t = condition_pars(rx['conditions']['temperature'])
            # file_name = file + '.csv'
            try:
                file_name = os.path.join(ntpath.dirname(file),
                                         ntpath.basename(file).split('.')
                                         [0]) + f"_{rx['name']}" + '.csv'
                _ = Reaction(name=rx['name'],
                             compounds=compounds,
                             reaction=rx['reaction'],
                             condition={
                                 'temperature': t,
                                 'pressure': p
                             })

                _.g_reaction().to_csv(path_or_buf=file_name)

            except Exception as err:
                print(f'trouble in {rx}')
                raise err


cli = click.CommandCollection(sources=[cli1])

if __name__ == '__main__':
    cli()
