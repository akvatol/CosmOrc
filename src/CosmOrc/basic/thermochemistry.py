import logging
from itertools import count
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

import src.CosmOrc.parsers.gauspar as gauspar
import src.CosmOrc.parsers.orpar as orpar
from src.CosmOrc.parsers.cospar import Jobs

R = 8.31441
h = 6.626176e-34
kB = 1.380662e-23  # J/K
N0 = 6.022_140_85774e-23  # 1/mol

PROGRAM_LIST = ('orca', 'gaussian')

# code from https://docs.python.org/3/howto/logging-cookbook.html
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log', mode='w')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
)
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')


class Compound:

    _ids = count(1)
    # __slots__ = []

    def __init__(self,
                 qm_program: str = 'gaussian',
                 qm_data: pd.Series = None,
                 path_to_file: str = None,
                 linear: bool = False,
                 atom: bool = False,
                 name: str = None,
                 sn: int = 1):

        # class instance counter
        self.id = next(self._ids)

        self.qm_program = qm_program

        if name:
            self.name = name
        else:
            self.name = str(self.id)

        if path_to_file:
            self.file = path_to_file
        else:
            _msg = 'compound {} is missing a file'.format(self.name)
            logger.error(_msg)
            raise TypeError(
                "__init__() missing 1 required positional argument: 'path_to_file'")

        if linear:
            self.linear_coefficient = 1.0
        else:
            self.linear_coefficient = 1.5

        self.atom = atom
        self.sn = sn

        try:
            if self.qm_program.lower() == 'gaussian':
                self.qm_data = gauspar.file_pars(self.file)
            elif self.qm_program.lower() == 'orca':
                self.qm_data = orpar.file_pars(self.file)
            else:
                _msg = f'Failed to load "{self.file}"'
                logger.error(_msg)
                print('This program does not supported in current version\n')
                print(PROGRAM_LIST)
                raise ValueError
        except Exception as err:
            _msg = '{} while parsing file {}'.format(repr(err), self.file)
            logger.error(_msg)
            raise err

        if self.qm_data['natoms'] == 2:

            if self.linear_coefficient == 1.5:
                print(f'{self.name}:\n')
                print(
                    'Warning! The molecule consists of two atoms, but is marked as non-linear.\n')
                _msg = f'{self.name} molecule marked as non-linear, but have only 2 atoms'
                logger.warning(_msg)

            # Если молекула 2х атомная, то в ней 1 частота
            # Нужно чтобы вернуло не 1 значение, а список
            self.freqs = np.array([self.qm_data['freq.']])
        elif self.qm_data['atom']:
            self.freqs = np.array([0])
        else:
            self.freqs = self.qm_data['freq.']

        if not self.atom:
            self.vib_temp = np.fromiter(
                map(lambda x: 299792458 / (1 / x / 100) * 4.79924466221135e-11,
                    self.freqs), np.float64)
        else:
            # Если нет частот, то не пытаемся пересчитать
            self.vib_temp = np.array([0])

    @classmethod
    def from_dict(cls, some_dict: dict):

        return cls(
            qm_program=some_dict.get('qm_program', 'gaussian'),
            path_to_file=some_dict.get('path_to_file'),
            linear=some_dict.get('linear', False),
            atom=some_dict.get('atom', False),
            name=some_dict.get('name'),
            sn=some_dict.get('sn', 1))

    @classmethod
    def from_series(cls, series: pd.Series, name: str, sn: int = 1):
        print('Проверьте правильность данных в таблице\n')
        try:
            return cls(
                qm_program=series.loc['qm_program'],
                linear=series.loc['linear'],
                atom=series.loc['atom'],
                qm_data=series,
                name=name,
                sn=sn)
        except Exception as err:
            # TODO
            _msg = f'initialization error in {name}'
            logger.error(_msg)
            raise err


def vib_temp_t(compound: Compound, temperature: np.array) -> np.array:
    """[summary]

    Parameters
    ----------
    compound : Compound
        [description]
    temperature : np.array
        [description]

    Returns
    -------
    np.array
        [description]
    """
    # WORk

    # Ui = vi/T

    freq = compound.vib_temp
    vib = []

    # TODO исправить чтобы работало для одной температуры
    for t in temperature:
        vib.append(freq / t)
    return np.array(vib)  # 2 dimensional np.array


def vibrational_enthalpy(compound: Compound, temperature: np.array,
                         pressure: np.array) -> np.array:
    """[summary]

    Parameters
    ----------
    compound : Compound
        [description]
    temperature : np.array
        [description]
    pressure : np.array
        [description]

    Returns
    -------
    np.array
        [description]
    """
    # WORK
    # Hv = N0*h∑(vi/(expUi - 1))

    _hvs = map(
        lambda x: R * np.sum(compound.vib_temp / np.expm1(x) + 0.5 * compound.
                             vib_temp), vib_temp_t(compound, temperature))

    df = pd.DataFrame(
        index=pressure,
        columns=temperature,
        data=[np.fromiter(_hvs, np.float)] * len(pressure))

    return df


def enthalpy(compound: Compound, temperature: np.array,
             pressure: np.array) -> np.array:
    """[summary]

    Parameters
    ----------
    compound : Compound
        [description]
    temperature : np.array
        [description]
    pressure : np.array
        [description]

    Returns
    -------
    np.array
        [description]
    """
    # WORK
    # gaussian
    # Hcorr = Etot + kB*T
    # kB = 1.380649e-23 J/K (Boltzmann constant)

    # Panin`s book
    # H(T) = Ht + Hr + Hv + E0 + R*T
    # E0 - Полная электронная энергия
    # Ht = Hr = 1.5*R*T for nonlinear molecules
    # Hr = R*T for linear molecules
    # Hv = N0*h∑(vi/(expUi - 1))

    Ht = 1.5 * R * temperature
    rt = R * temperature

    if compound.linear_coefficient == 1:
        Hr = rt
    else:
        Hr = Ht

    # Check if compound have only 1 atom
    if compound.atom:
        Hv = 0
        Hr = 0
    else:
        Hv = vibrational_enthalpy(
            compound=compound, temperature=temperature, pressure=pressure)

    Htot = Ht + Hr + rt + compound.qm_data['scf energy']

    df = pd.DataFrame(
        index=pressure, columns=temperature, data=[Htot] * len(pressure))

    return df + Hv


def translation_entropy(compound: Compound, temperature: np.array,
                        pressure: np.array) -> np.array:
    """[summary]

    Parameters
    ----------
    compound : Compound
        [description]
    temperature : np.array
        [description]
    pressure : np.array
        [description]

    Returns
    -------
    np.array
        [description]
    """
    # WORK
    # https://mipt.ru/dbmp/utrapload/566/OXF_3-arphlf42s21.pdf
    # 3.18 eq
    # St = 1.5*R*ln(M) + 2.5*R*ln(T) - R*ln(P) - 9.69
    # M - g/mol, T - K, P - atm

    Ts = []
    for p in pressure:
        _ = (R * (1.5 * np.log(compound.qm_data['molecular mass']) + 2.5 * np.log(temperature) -
                  np.log(p)) - 9.69)
        Ts.append(_)

    df = pd.DataFrame(index=pressure, columns=temperature, data=Ts)

    return df


def rotational_entropy(compound: Compound, temperature: np.array,
                       pressure: np.array) -> np.array:
    """[summary]

    Parameters
    ----------
    compound : Compound
        [description]
    temperature : np.array
        [description]
    pressure : np.array
        [description]

    Returns
    -------
    np.array
        [description]
    """
    # WORK

    # Sr = R*(ln(qr) + 1.5) for nonlinear molecules
    # Sr = R*(ln(qr) + 1) for linear molecules
    # y = (exp(Sr0/R - x)/T0**x)
    # qr = y*T**x
    if compound.qm_program == 'gaussian':
        srot = compound.qm_data['rotational entropy']
    elif compound.qm_program == 'orca':
        srot = compound.qm_data[f'{compound.sn} s(rot)'] / \
            compound.qm_data['temperature']

    y = np.exp(srot / R - compound.linear_coefficient
               ) / compound.qm_data['temperature']**compound.linear_coefficient
    qr = y * temperature**compound.linear_coefficient
    index = pressure
    columns = temperature
    data = [R * (np.log(qr) + compound.linear_coefficient)] * len(pressure)

    try:
        df = pd.DataFrame(
            index=index,
            columns=columns,
            data=data)
        return df
    except Exception as e:
        error_txt = f'\nError: {e}\n index:{index},\n columns:{columns}\n data:{data}\n'
        raise Exception(error_txt)


def vibrational_entropy(compound: Compound, temperature: np.array,
                        pressure: np.array) -> np.array:
    """[summary]

    Parameters
    ----------
    compound : Compound
        [description]
    temperature : np.array
        [description]
    pressure : np.array
        [description]

    Returns
    -------
    np.array
        [description]
    """
    # WORK

    Ua = vib_temp_t(compound, temperature)
    svib = map(
        lambda x: R * np.sum((x / np.expm1(x)) - np.log(1 - np.exp(-x))), Ua)

    df = pd.DataFrame(
        index=pressure,
        columns=temperature,
        data=[np.fromiter(svib, np.float)] * len(pressure))

    return df


def total_entropy(compound: Compound, temperature: np.array,
                  pressure: np.array) -> np.array:
    """[summary]

    Parameters
    ----------
    compound : Compound
        [description]
    temperature : np.array
        [description]
    pressure : np.array
        [description]

    Returns
    -------
    np.array
        [description]
    """
    # Stot = St + Sr + Sv + Se

    # Se = R*LnW - const

    Se = compound.qm_data['electronic entropy']
    if compound.atom:
        Sv = 0
        Sr = 0
    else:
        Sr = rotational_entropy(
            compound=compound, temperature=temperature, pressure=pressure)
        Sv = vibrational_entropy(
            compound=compound, temperature=temperature, pressure=pressure)

    St = translation_entropy(
        compound=compound, temperature=temperature, pressure=pressure)

    return (St + Sr + Sv + Se)


def gibbs_energy(compound: Compound, temperature: np.array,
                 pressure: np.array) -> np.array:
    """[summary]

    Parameters
    ----------
    compound : Compound
        [description]
    temperature : np.array
        [description]
    pressure : np.array
        [description]

    Returns
    -------
    np.array
        [description]
    """
    # Gcorr = Hcorr - T*Stot
    # G = H(T) - T*Stot

    return enthalpy(
        compound=compound, temperature=temperature,
        pressure=pressure) - temperature * total_entropy(
            compound=compound, temperature=temperature, pressure=pressure)


class Reaction:
    _ids = count(1)
    # __slots__ = []

    def __init__(self,
                 reaction: Tuple[Dict[str, Tuple[float, Compound]], ...],
                 name: str = None):

        self.id = next(self._ids)

        if name:
            self.name = name
        else:
            self.name = str(self.id)

        self.reaction = reaction

    @classmethod
    def from_dict(cls, some_dict: Dict):
        pass


def str_pars(some_str: str):

    if len(some_str.strip().split()) == 3:
        step = float(some_str.strip().split()[2])
        start = float(some_str.strip().split()[0])
        stop = float(some_str.strip().split()[1]) + step
    elif len(some_str.strip().split()) == 2:
        step = 1
        start = float(some_str.strip().split()[0])
        stop = float(some_str.strip().split()[1]) + step
    elif len(some_str.strip().split()) == 1:
        step = 1
        start = float(some_str.strip().split()[0])
        stop = float(some_str.strip().split()[0])

    return np.asarray(np.arange(start, stop, step), dtype='float64')


def tp_pars(condition: Dict[str, str]) -> Tuple[np.array, np.array, ]:

    _t = str_pars(condition.get('temperature', '298.15'))
    _p = str_pars(condition.get('pressure', '1'))
    return(_t, _p)


def gibbs_semi_reaction_gas(
        semi_reaction: Dict[str, Tuple[float, Compound]],
        condition: Tuple[np.array, ...]) -> pd.DataFrame:

    temperature = condition[0]
    pressure = condition[1]

    g = 0

    for compound in semi_reaction.keys():
        g += semi_reaction[compound][0]*gibbs_energy(
            compound=semi_reaction[compound][1],
            temperature=temperature,
            pressure=pressure)

    return g


def gibbs_energy_gas(
        condition: Tuple[np.array, ...],
        reaction_list: Tuple[Dict[str, Tuple[float, Compound]], ...]):

    # Считаем dG реакции в вакуме

    G_react = gibbs_semi_reaction_gas(
        semi_reaction=reaction_list[0],
        condition=condition)

    G_prod = gibbs_semi_reaction_gas(
        semi_reaction=reaction_list[1],
        condition=condition)
    return G_prod - G_react

def ggas_generate_cosmo():
    pass

def main_calc(
        condition: dict,
        reaction: Reaction,
        condition_cosmo: bool = False,
        solubility_cosmo: bool = False):

    if not condition_cosmo:
        _condition = tp_pars(condition)
        g = gibbs_energy_gas(
            reaction_list=reaction.reaction,
            condition=_condition)
    elif condition_cosmo and solubility_cosmo:
        pass
    elif condition_cosmo:
        pass

    return g
