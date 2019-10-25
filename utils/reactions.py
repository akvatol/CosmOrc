from itertools import count
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

import utils.gauspar as gauspar
import utils.orpar as orpar
from utils.cospar import Jobs

R = 8.31441
h = 6.626176e-34
kB = 1.380662e-23  # J/K
N0 = 6.022_140_85774e-23  # 1/mol

PROGRAM_LIST = ('orca', 'gaussian')


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
        self.atom = atom
        self.sn = sn
        self.path_to_file = path_to_file

        if name:
            self.name = name
        else:
            self.name = str(self.id)

        if path_to_file:
            self.file = path_to_file
        else:
            _msg = 'compound {} is missing a file'.format(self.name)
            # logger.error(_msg)
            raise TypeError(
                "__init__() missing 1 required positional argument: 'path_to_file'"
            )

        if linear:
            self.linear_coefficient = 1.0
        else:
            self.linear_coefficient = 1.5

        try:
            if self.qm_program.lower() == 'gaussian':
                self.qm_data = gauspar.file_pars(self.file)
            elif self.qm_program.lower() == 'orca':
                self.qm_data = orpar.file_pars(self.file)
            else:
                _msg = f'Failed to load "{self.file}"'
                # logger.error(_msg)
                print('This program does not supported in current version\n')
                # print(PROGRAM_LIST)
                raise ValueError
        except Exception as err:
            _msg = '{} while parsing file {}'.format(repr(err), self.file)
            # logger.error(_msg)
            raise err

        if self.qm_data['natoms'] == 2:

            if self.linear_coefficient == 1.5:
                print(f'{self.name}:\n')
                print(
                    'Warning! The molecule consists of two atoms, but is marked as non-linear.\n'
                )
                _msg = f'{self.name} molecule marked as non-linear, but have only 2 atoms'
                # logger.warning(_msg)

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

    def __repr__(self):
        return self.path_to_file

    @classmethod
    def from_dict(cls, some_dict: dict):

        return cls(qm_program=some_dict.get('qm_program', 'gaussian'),
                   path_to_file=some_dict.get('path_to_file'),
                   linear=some_dict.get('linear', False),
                   atom=some_dict.get('atom', False),
                   name=some_dict.get('name'),
                   sn=some_dict.get('sn', 1))

    @classmethod
    def from_series(cls, series: pd.Series, name: str, sn: int = 1):
        print('Проверьте правильность данных в таблице\n')
        try:
            return cls(qm_program=series.get('qm_program', 'gaussian'),
                       linear=series.get('linear', False),
                       atom=series.get('atom', False),
                       qm_data=series,
                       name=name,
                       sn=sn)
        except Exception as err:
            # TODO
            _msg = f'initialization error in {name}'
            # logger.error(_msg)
            raise err

    def vib_temp_t(self, temperature: np.array) -> np.array:
        return np.array(list(map(lambda f: f / temperature, self.vib_temp))).T

    def vibrational_enthalpy(self, temperature: np.array,
                             pressure: np.array) -> np.array:
        _hvs = map(
            lambda x: R * np.sum(self.vib_temp / np.expm1(x) + 0.5 * self.
                                 vib_temp), self.vib_temp_t(temperature))

        df = pd.DataFrame(index=pressure,
                          columns=temperature,
                          data=[np.fromiter(_hvs, np.float)] * len(pressure))

        return df

    def enthalpy(self, temperature: np.array, pressure: np.array) -> np.array:
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

        if self.linear_coefficient == 1:
            Hr = rt
        else:
            Hr = Ht

        # Check if compound have only 1 atom
        if self.atom:
            Hv = 0
            Hr = 0
        else:
            Hv = self.vibrational_enthalpy(temperature=temperature,
                                           pressure=pressure)

        Htot = Ht + Hr + rt + self.qm_data.get('scf energy')

        df = pd.DataFrame(index=pressure,
                          columns=temperature,
                          data=[Htot] * len(pressure))

        return df + Hv

    def translation_entropy(self, temperature: np.array,
                            pressure: np.array) -> np.array:

        # WORK
        # https://mipt.ru/dbmp/utrapload/566/OXF_3-arphlf42s21.pdf
        # 3.18 eq
        # St = 1.5*R*ln(M) + 2.5*R*ln(T) - R*ln(P) - 9.69
        # M - g/mol, T - K, P - atm

        Ts = np.array(
            list(
                map(
                    lambda p:
                    (R *
                     (1.5 * np.log(self.qm_data.get('Molecular mass')) + 2.5 *
                      np.log(temperature) - np.log(p)) - 9.69), pressure)))

        df = pd.DataFrame(index=pressure, columns=temperature, data=Ts)

        return df

    def rotational_entropy(self, temperature: np.array,
                           pressure: np.array) -> np.array:
        # WORK

        # Sr = R*(ln(qr) + 1.5) for nonlinear molecules
        # Sr = R*(ln(qr) + 1) for linear molecules
        # y = (exp(Sr0/R - x)/T0**x)
        # qr = y*T**x

        if self.qm_program == 'gaussian':
            srot = self.qm_data.get('Rotational Entropy')
        elif self.qm_program == 'orca':
            srot = self.qm_data[f'{self.sn} s(rot)'] / \
                self.qm_data.get('Temperature', 298.15)

        y = np.exp(srot / R - self.linear_coefficient
                   ) / self.qm_data['Temperature']**self.linear_coefficient
        qr = y * temperature**self.linear_coefficient
        index = pressure
        columns = temperature
        data = [R * (np.log(qr) + self.linear_coefficient)] * len(pressure)

        try:
            df = pd.DataFrame(index=index, columns=columns, data=data)
            return df
        except Exception as e:
            error_txt = f'\nError: {e}\n index:{index},\n columns:{columns}\n data:{data}\n'
            raise Exception(error_txt)

    def vibrational_entropy(self, temperature: np.array,
                            pressure: np.array) -> np.array:
        Ua = self.vib_temp_t(temperature)
        svib = map(
            lambda x: R * np.sum((x / np.expm1(x)) - np.log(1 - np.exp(-x))),
            Ua)

        df = pd.DataFrame(index=pressure,
                          columns=temperature,
                          data=[np.fromiter(svib, np.float)] * len(pressure))

        return df

    def total_entropy(self, temperature: np.array,
                      pressure: np.array) -> np.array:
        # Stot = St + Sr + Sv + Se

        # Se = R*LnW - const

        Se = self.qm_data.get('Electronic Entropy', 0)
        if self.atom:
            Sv = 0
            Sr = 0
        else:
            Sr = self.rotational_entropy(temperature=temperature,
                                         pressure=pressure)
            Sv = self.vibrational_entropy(temperature=temperature,
                                          pressure=pressure)

        St = self.translation_entropy(temperature=temperature,
                                      pressure=pressure)

        return (St + Sr + Sv + Se)

    def gibbs_energy(self, temperature: np.array,
                     pressure: np.array) -> np.array:
        return self.enthalpy(
            temperature=temperature,
            pressure=pressure) - temperature * self.total_entropy(
                temperature=temperature, pressure=pressure)


class Reaction:
    def __init__(self,
                 reaction: str,
                 compounds: List[Compound],
                 condition: Dict[str, np.array] = None,
                 name: str = None):

        if name:
            self.name = name
        else:
            self.name = reaction

        if condition:
            self.condition = condition
        else:
            self.condition = {
                'temperature': np.array([298.15]),
                'pressure': np.array([1])
            }

        self.reaction = reaction
        self.compounds = compounds
        self.reaction_dict = self.reaction_pars(reaction=self.reaction,
                                                compounds=self.compounds)

    def reaction_pars(self, reaction: str, compounds: List[Compound]
                      ) -> List[Dict[str, Tuple[float, Compound]]]:
        # element[0] - reagents, elements[1] - products
        # reaction look like '2*A + 3*C = D'
        reaction_dict: List[Dict[str, Tuple[float, Compound]]] = []
        _compounds_dict: Dict[str, Compound] = {x.name: x for x in compounds}
        for element in reaction.split('='):
            half_reaction: Dict[str, Tuple[float, Compound]] = {}
            for compound in element.split('+'):
                # compound look like '2*S'
                if '*' in compound:
                    coefficient = float(compound.split('*')[0].strip())
                    compound_name = compound.split('*')[1].strip()
                    half_reaction[compound_name] = (
                        coefficient, _compounds_dict[compound_name])
                else:
                    compound_name = compound.strip()
                    half_reaction[compound.strip()] = (
                        1, _compounds_dict[compound_name])
            # где dict_repr_reaction[0] - словарь {имя в-ва: коэффициент} c реагентами
            # dict_repr_reaction[1] - аналогичный словарь для продуктов р-ции
            reaction_dict.append(half_reaction)
        return reaction_dict

    # TODO: Можно заменить функцию лямбой полностью
    def _g_half_reaction(self,
                         half_reaction: Dict[str, Tuple[float, Compound]],
                         condition: Dict[str, np.array]) -> pd.DataFrame:
        # g = 0
        # for compound in half_reaction.keys():
        #     g += half_reaction[compound][0]*half_reaction[compound][1].gibbs_energy(temperature=condition.get(
        #         'temperature', np.array([298.15])), pressure=condition.get('pressure', np.array([1])))
        # return g
        return sum(
            map(
                lambda compound: half_reaction[compound][0] * half_reaction[
                    compound][1].gibbs_energy(temperature=condition.get(
                        'temperature', np.array([298.15])),
                                              pressure=condition.get(
                                                  'pressure', np.array([1]))),
                half_reaction.keys()))

    def g_reaction(self) -> pd.DataFrame:

        reaction_dict = self.reaction_pars(reaction=self.reaction,
                                           compounds=self.compounds)

        g_prod = self._g_half_reaction(half_reaction=reaction_dict[1],
                                       condition=self.condition)

        g_reag = self._g_half_reaction(half_reaction=reaction_dict[0],
                                       condition=self.condition)

        return g_prod - g_reag

# Coming soon
class Reaction_COSMO:
    def __init__(self,
                 reaction: str,
                 compounds: List[Compound],
                 cosmo: list,
                 condition: Dict[str, np.array] = None,
                 name: str = None,
                 ideal: list = None,
                 gases: list = None,
                 solids: list = None):

        pass


#%%
def main():
    Br = Compound.from_dict({
        'name': 'Br',
        'path_to_file':
        '/media/antond/87B6-87D6/mn15l_def2tzvp/Anions/Br/Br.log',
        'atom': True
    })
    BiBr6 = Compound.from_dict({
        'name':
        'BiBr6',
        'path_to_file':
        '/media/antond/87B6-87D6/mn15l_def2tzvp/Anions/BiBr6/BiBr6.log'
    })
    Bi2Br9 = Compound.from_dict({
        'name':
        'Bi2Br9',
        'path_to_file':
        '/media/antond/87B6-87D6/mn15l_def2tzvp/Anions/Bi2Br9/bi2br9.log'
    })
    Bi2Br10 = Compound.from_dict({
        'name': 'Bi2Br10',
        'path_to_file': ''
    })
    Bi3Br14z = Compound.from_dict({})
    Bi3Br14str = Compound.from_dict({})
    BiBr6D = Compound.from_dict({})
    Bi2Br9D = Compound.from_dict({})
    Bi2Br10D = Compound.from_dict({})
    Bi3Br14zD = Compound.from_dict({})
    Bi3Br14strD = Compound.from_dict({})
    dimethylazanium = Compound.from_dict({})
    cond = {
        'temperature': np.array([i for i in range(250, 360, 10)]),
        'pressure': np.array([1])
    }
    r = Reaction_COSMO(cosmo=None,
                       reaction='2*BiBr6 = Bi2Br9 + 3*Br',
                       condition=cond,
                       compounds=[Br, BiBr6, Bi2Br9])
    std = {'temperature': np.array([298.15]), 'pressure': np.array([1])}

    # return Bi2Br9.gibbs_energy(temperature=np.array([298.15]), pressure=np.array([1])) - Bi2Br9.qm_data['sum of electronic and thermal free energies']
    # return (r._g_half_reaction(half_reaction=r.reaction_dict[0], condition=std), 2*BiBr6.gibbs_energy(temperature=np.array([298.15]), pressure=np.array([1])))
    # return (r._g_half_reaction(half_reaction=r.reaction_dict[1], condition=std), Bi2Br9.gibbs_energy(temperature=np.array([298.15]), pressure=np.array([1])) + 3*Br.gibbs_energy(temperature=np.array([298.15]), pressure=np.array([1])))
    # return r.reaction_dict

    return r.g_reaction()


#%%
