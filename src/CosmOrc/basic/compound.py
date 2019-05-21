import numpy as np
import pandas as pd

from typing import Callable, Iterable, Union, Optional, List

import src.CosmOrc.parsers.gauspar as gauspar

R = 8.31441
h = 6.626176e-34
kB = 1.380662e-23  # J/K
N0 = 6.022_140_85774e-23  # 1/mol


# TODO Навести в коде порядок и сделать проверку на None
class Compound:

    __slots__ = ('qm_data', 'name', 'linear', 'E0', 'stat_sum', 'path_to_file',
                 'sn', 'atom', 'qm_program', 'mass', 'vib_temp', 'freqs', 'ideal')

    def __init__(self,
                 path_to_file: str = None,
                 name: str = None,
                 qm_program: str = None,
                 ideal: bool = None,
                 linear: bool = None,
                 atom: bool = None,
                 sn: int = None):

        self.name = name
        self.path_to_file = path_to_file
        self.sn = sn

        if qm_program:
            self.qm_program = qm_program
        else:
            self.qm_program = 'gaussian'

        if linear:
            self.linear = 1.0
        else:
            self.linear = 1.5

        self.ideal = ideal

        if self.qm_program.lower() == 'gaussian':
            self.qm_data = gauspar.file_pars(path_to_file)

        elif self.qm_program.lower() == 'orca':
            raise Exception(
                'This option is not supported in this version of the program.')

        self.mass = self.qm_data['Molecular mass']
        self.atom = atom

        self.E0 = self.qm_data['SCF Energy']
        # TODO Поправил для расчета атомов
        # TODO Добавил частоты
        self.freqs = self.qm_data['freq.']
        self.freqs = self.freqs[self.freqs > 0].dropna()

        if not self.atom:
            self.vib_temp = np.fromiter(
                map(lambda x: 299792458 / (1 / x / 100) * 4.79924466221135e-11,
                    self.freqs), np.float64)
        else:
            # Если нет частот, то не пытаемся пересчитать
            self.vib_temp = np.array([0])

    def __repr__(self):
        _representation = f"Compound(path_to_file='{self.path_to_file}', "\
                          f"name='{self.name}', "\
                          f"qm_program='{self.qm_program}', "\
                          f"linear={self.linear}, "\
                          f"atom={self.atom}, "\
                          f"sn={self.sn})"
        return _representation

    def __str__(self):
        return self.name

    @classmethod
    def from_dict(cls, some_dict: dict):

        return cls(
            name=some_dict.get('name'),
            path_to_file=some_dict.get('path_to_file'),
            qm_program=some_dict.get('qm_program'),
            linear=some_dict.get('linear'),
            sn=some_dict.get('sn'),
            atom=some_dict.get('atom'))


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


def enthalpy(compound: Compound, temperature: np.array = None,
             pressure: np.array = None) -> np.array:
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

    if not temperature:
        temperature = np.array([298.15])
    
    if not pressure:
        pressure = np.array([1])

    Ht = 1.5 * R * temperature
    rt = R * temperature

    if compound.linear == 1:
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

    Htot = Ht + Hr + rt + compound.E0

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
    # https://mipt.ru/dbmp/upload/566/OXF_3-arphlf42s21.pdf
    # 3.18 eq
    # St = 1.5*R*ln(M) + 2.5*R*ln(T) - R*ln(P) - 9.69
    # M - g/mol, T - K, P - atm

    Ts = []
    for p in pressure:
        _ = (R * (1.5 * np.log(compound.mass) + 2.5 * np.log(temperature) -
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

    y = np.exp(compound.qm_data['Rotational Entropy'] / R - compound.linear
               ) / compound.qm_data['Temperature']**compound.linear
    qr = y * temperature**compound.linear
    index = pressure
    columns = temperature
    data = [R * (np.log(qr) + compound.linear)] * len(pressure)

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


def total_entropy(compound: Compound, temperature: np.array = None,
                  pressure: np.array = None) -> np.array:
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

    if not temperature:
        temperature = np.array([298.15])

    if not pressure:
        pressure = np.array([1])

    Se = compound.qm_data['Electronic Entropy']
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


def gibbs_energy(compound: Compound, temperature: np.array = None,
                 pressure: np.array = None) -> np.array:
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

    if not temperature:
        temperature = np.array([298.15])

    if not pressure:
        pressure = np.array([1])

    return enthalpy(
        compound=compound, temperature=temperature,
        pressure=pressure) - temperature * total_entropy(
            compound=compound, temperature=temperature, pressure=pressure)


# %%
def main():
#     import os
# 
#     temperature = np.array([313.15, 323.15, 333.15, 343.15, 353.15, 363.15])  # np.arange(300, 400 + 5, 5)
#     pressure = np.array([1])  # p.arange(1, 10 + 0.1, 0.1)
# 
#     with open('pasha.csv', 'w') as dump:
#         for files in os.listdir("/home/antond/Загрузки/archive/"):
#             for temperatures in temperature:
#                 try:
#                     if 'hbr' in files:
#                         Comp = {
#                             'name': files,
#                             'path_to_file': "/home/antond/Загрузки/archive/" + files,
#                             'linear': True
#                         }
#                         a = Compound.from_dict(Comp)
#                         g_energy = gibbs_energy(
#                             compound=a, temperature=np.array([temperatures]), pressure=pressure)[temperatures].loc[1]
#                     else:
#                         Comp = {
#                             'name': files,
#                             'path_to_file': "/home/antond/Загрузки/archive/" + files,
#                             'linear': False
#                         }
#                         a = Compound.from_dict(Comp)
#                         g_energy = gibbs_energy(
#                             compound=a, temperature=np.array([temperatures]), pressure=pressure)[temperatures].loc[1]
# 
#                     string = f'File:\t{files}, GibbsEnergy=\t{g_energy}, T={temperatures}\n'
#                 except:
#                     print(a.freqs)
#                     string = f'Error in\t{files}\n'
#                 dump.write(string)
    pass
    # Искал ошибку
    # files = "/home/antond/projects/HL/TS4c-4d.log"
    # Comp = {'name': files, 'path_to_file': files, 'linear': False}
    # a = Compound.from_dict(Comp)
    # g_energy = gibbs_energy(
    #     compound=a, temperature=temperature, pressure=pressure)[398.15].loc[1]
    # c = rotational_entropy(
    #     compound=a, temperature=temperature, pressure=pressure)
    # print(c)
    # string = f'File: {files}, Gibbs Energy = {g_energy}, condition=({temperature}, {pressure}) \n'


if __name__ == '__main__':
    main()

