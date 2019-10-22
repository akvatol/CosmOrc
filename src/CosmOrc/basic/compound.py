import numpy as np
import pandas as pd

from typing import Callable, Iterable, Union, Optional, List

import src.CosmOrc.parsers.gauspar as gauspar
import src.CosmOrc.parsers.orpar as orpar

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


        self.qm_program = qm_program

        if linear:
            self.linear = 1.0
        else:
            self.linear = 1.5

        self.ideal = ideal

        if self.qm_program == 'gaussian':
            self.qm_data = gauspar.file_pars(path_to_file)

        elif self.qm_program == 'orca':
            self.qm_data = orpar.file_pars(path_to_file)

        self.mass = self.qm_data['molecular mass']
        self.atom = atom

        self.E0 = self.qm_data['scf energy']
        # TODO Поправил для расчета атомов
        # TODO Добавил частоты
        if self.qm_data['deg. of freedom'] == 1:
            self.freqs = np.array([self.qm_data['freq.']])
        elif self.qm_data['atom'] == True:
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
    # https://mipt.ru/dbmp/utrapload/566/OXF_3-arphlf42s21.pdf
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

    y = np.exp(compound.qm_data['rotational entropy'] / R - compound.linear
               ) / compound.qm_data['temperature']**compound.linear
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


# %%
# def main():
#     path = '/media/antond/87B6-87D6/Scamt_Project/mn15l_def2tzvp/ion_pairs/'
#     folder = '4-methylpyridin-1-ium'
# 
#     Br_dict = {'name': 'Br', 'atom': True,
#                'path_to_file': '/home/antond/mn15l_def2tzvp/Anions/Br/Br.log'}
#     BiBr6_dict = {'name': 'BiBr6',
#                   'path_to_file': '/home/antond/mn15l_def2tzvp/Anions/BiBr6/BiBr6.log'}
# 
#     cation_dict={'path_to_file':'/home/antond/mn15l_def2tzvp/Cations/4-methylpyridin-1-ium/4-methylpyridin-1-ium.log'}
#     # cation_dict={'path_to_file':'/home/antond/mn15l_def2tzvp/Cations/dimethylazanium/dimethylazanium.log'}
# 
#     c1_dict = {'path_to_file': path + folder + '/1/1.log'}
#     c21_dict = {'path_to_file': path + folder + '/21/21.log'}
#     c22_dict = {'path_to_file': path + folder + '/22/22.log'}
#     c23_dict = {'path_to_file': path + folder + '/23/23.log'}
#     c31_dict = {'path_to_file': path + folder + '/31/31.log'}
#     c32_dict = {'path_to_file': path + folder + '/32/32.log'}
#     c33_dict = {'path_to_file': path + folder + '/33/33.log'}
# 
#     Br = Compound.from_dict(Br_dict)
#     BiBr6 = Compound.from_dict(BiBr6_dict)
#     Cat = Compound.from_dict(cation_dict)
# 
#     c1 = Compound.from_dict(c1_dict)
#     c21 = Compound.from_dict(c21_dict)
#     c22 = Compound.from_dict(c22_dict)
#     c23 = Compound.from_dict(c23_dict)
#     c31 = Compound.from_dict(c31_dict)
#     c32 = Compound.from_dict(c32_dict)
#     c33 = Compound.from_dict(c33_dict)
# 
#     t = np.array([x for x in range(250, 360, 10)])
#     p = np.array([1])
# 
#     Gc1 = gibbs_energy(compound=c1, temperature=t, pressure=p)
#     Gc21 = gibbs_energy(compound=c21, temperature=t, pressure=p)
#     Gc22 = gibbs_energy(compound=c22, temperature=t, pressure=p)
#     Gc23 = gibbs_energy(compound=c23, temperature=t, pressure=p)
#     Gc31 = gibbs_energy(compound=c31, temperature=t, pressure=p)
#     Gc32 = gibbs_energy(compound=c32, temperature=t, pressure=p)
#     Gc33 = gibbs_energy(compound=c33, temperature=t, pressure=p)
# 
#     Gcat = gibbs_energy(compound=Cat, temperature=t, pressure=p)
#     GBiB6 = gibbs_energy(compound=BiBr6, temperature=t, pressure=p)
#     GBr = gibbs_energy(compound=Br, temperature=t, pressure=p)
# 
#     df = Gc31 - Gc23 - Gcat
# 
#     df.to_csv(path_or_buf='14.csv', sep='\t')


# if __name__ == '__main__':
#     main()




#%%
