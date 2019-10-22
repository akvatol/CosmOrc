import glob
import logging
import os
import random

import numpy as np
import pandas as pd

from typing import List, Set, Dict, Tuple, Any
from typing import Callable, Iterable, Union, Optional, List

from src.CosmOrc.basic.compound import Compound

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


class Reaction:
    # __slots__ = ()
    def __init__(self,
                 name: str,
                 reaction: Tuple[Dict[Compound, int], ...],
                 condition: Dict[str, float],
                 cosmo_rs_condition: Tuple[str] = None):

        self.name = name

        if reaction:
            # TODO Что-нибудь сделать
            self.reaction = reaction
        else:
            logger.error(f'Reaction: {(self.name)} have no reaction parameter')

        self.cosmo_rs = None

        if condition:
            self.temperature = condition['temperature']
            self.pressure = condition['pressure']
        elif cosmo_rs_condition:
            # TODO: Сделать
            # self.temperature = cosmo_rs_condition['temperature']
            # self.pressure = cosmo_rs_condition['pressure']
            # self.cosmo_rs = data from cospar
            pass
        else:
            pass

        logger.info(f'{self} was created successfully')

    def __repr__(self):
        _representation = f'Reaction(name={self.name}, reaction={self.reaction})'
        return _representation

    def __add__(self, other):
        if isinstance(other, Compound):
            pass
        else:
            # TODO Написать нормальный текст для ошибки
            Error_text = f'Error: __add__({self}, {other})'
            raise Exception(Error_text)

    def __sub__(self, other):
        if isinstance(other, Compound):
            pass
        else:
            # TODO Написать нормальный текст для ошибки
            Error_text = f'Error: __sub__({self}, {other})'
            raise Exception(Error_text)

    @classmethod
    def from_dict(cls, reaction_dict: Dict[str, str]):
        name: str = reaction_dict.get('name')
        reaction: Tuple[Dict[Compound, int], ...] = chemical_equation_pars(
            reaction_dict.get('reaction'))
        # TODO Сделать
        if reaction_dict.get('condition'):
            condition = condition_pars(reaction_dict.get('condition'))
            return cls(name=name,
                       reaction=reaction,
                       condition=condition)
        elif reaction_dict.get('condition_cosmo'):
            condition = reaction_dict.get('condition_cosmo')

    def _gibbs_energy(self):
        pass

    def _gibbs_energy_cosmo_(self):
        pass

    def calculate_gibbs_energy(self,
                               conditions: pd.DataFrame = None,
                               data_from_cosmo: pd.DataFrame = None,
                               settings_from_cosmo: pd.DataFrame = None):
        """[summary]

        Parameters
        ----------
        condition : pd.DataFrame, optional
            [description], by default None
        data_from_cosmo : pd.DataFrame, optional
            [description], by default None
        setting_from_cosmo : pd.DataFrame, optional
            [description], by default None

        Returns
        -------
        pd.DataFrame
            [description]
        """
        if conditions:
            pass
        elif data_from_cosmo and settings_from_cosmo:
            pass
        else:
            # TODO Написать текст
            Error_text = 'Some text'
            raise Exception(Error_text)
        return 0

    def calculate_enthalpy(self, conditions: pd.DataFrame = None):
        pass

    def calculate_entropy(self, conditions: pd.DataFrame = None):
        pass


# if condition_cosmo: true
def reaction_calc_cosmo(reaction_from_yaml: dict = None,
                        compounds: dict = None):
    _cosmo_data = []
    for path in reaction_from_yaml['condition']['path_to_files']:
        if os.path.isdir(path):
            for files in glob.glob(path + '*.tab'):
                _cosmo_data.append(Jobs(files))
        if os.path.isfile(path):
            _cosmo_data.append(Jobs(path))


# if condition_cosmo: false
def reaction_calc(reaction_from_yaml: dict = None,
                  parameter: str = None,
                  compounds: dict = None) -> pd.DataFrame:

    name = str(reaction_from_yaml['name'])
    reaction = chemical_equation_pars(reaction_from_yaml['reaction'])

    if compounds_check(
            compounds=compounds.keys(), reaction_dict_repr=reaction):
        pass

    condition = condition_pars(reaction_from_yaml['condition'])
    k = -3
    result = 0

    for semi_reaction in reaction:
        k += 2
        for compound_ in semi_reaction.keys():
            if parameter == 'H':
                result += k * semi_reaction[compound_] * entalpy(
                    temperature=np.array(
                        condition.loc['temperature'].dropna()),
                    pressure=np.array(condition.loc['pressure'].dropna()),
                    compound=compounds[compound_.strip()])

            else:
                try:
                    result += k * float(
                        semi_reaction[compound_]) * gibbs_energy(
                            temperature=np.array(
                                condition.loc['temperature'].dropna()),
                            pressure=np.array(
                                condition.loc['pressure'].dropna()),
                            compound=compounds[compound_.strip()])
                    return (name, result)
                except Exception as e:
                    t = condition.loc['temperature']
                    p = condition.loc['pressure']
                    s = f'temperature: {t}\n'\
                        f"pressure: {p}\n"\
                        f'Exception: {e}\n'
                    raise Exception(s)


def condition_pars(dict_conditions: dict = None):
    # Парсит условия и возвращает набор условий в виде DataFrame
    """[summary]

    Returns
    -------
    [type]
        [description]

    Raises
    ------
    Exception
        [description]
    """
    if dict_conditions:
        # TODO Написать комментарии
        _conditions = []
        for parameter in ('temperature', 'pressure'):
            value = 0
            if parameter in dict_conditions.keys():
                if len(dict_conditions[parameter].strip().split()) == 3:
                    step = float(dict_conditions[parameter].strip().split()[2])
                    start = float(
                        dict_conditions[parameter].strip().split()[0])
                    stop = float(
                        dict_conditions[parameter].strip().split()[1]) + step
                elif len(dict_conditions[parameter].strip().split()) == 2:
                    step = 1
                    start = float(
                        dict_conditions[parameter].strip().split()[0])
                    stop = float(
                        dict_conditions[parameter].strip().split()[1]) + step
                elif len(dict_conditions[parameter].strip().split()) == 1:
                    step = 1
                    start = float(
                        dict_conditions[parameter].strip().split()[0])
                    stop = float(
                        dict_conditions[parameter].strip().split()[0]) + step
                else:
                    raise Exception(
                        f'condition_pars(dict_conditions={dict_conditions})')
                value = np.arange(start, stop, step)
                value = np.asarray(value, dtype='float64')
            else:
                # TODO Костыль
                value = np.array([float(DEFAULT_CONDITION[parameter])])
                value = np.asarray(value, dtype='float64')
            # [[temperature], [pressure]]
            _conditions.append(value)
        try:
            conditions = pd.DataFrame(
                index=DEFAULT_CONDITION_NAMES, data=_conditions)
            return conditions
        except Exception as e:
            raise Exception(
                f'Exception:{e}, index={DEFAULT_CONDITION_NAMES}, data = {_conditions}'
            )


def compounds_check(compounds: list = None, reaction_dict_repr: list = None):
    """[summary]

    Parameters
    ----------
    compounds : tuple, optional
        [description], by default None
    reaction_dict_repr : tuple, optional
        [description], by default None

    Returns
    -------
    [type]
        [description]

    Raises
    ------
    Exception
        [description]
    """

    list_with_reactants = []
    # создаем список со всеми участниками реакции
    for semi_reaction in reaction_dict_repr:
        list_with_reactants += semi_reaction.keys()

    # Проверяет все ли вещества в участвующие реакции заданы
    if all(reactant in compounds for reactant in list_with_reactants):
        return True
    else:
        raise Exception(
            f'compounds: {compounds},' / f' reactants: {list_with_reactants}')


# TODO Нужно дочить и тестить
def compounds_init(list_with_compounds: list = None) -> dict:
    """[summary]

    Parameters
    ----------
    list_with_compounds : list, optional
        [description], by default None

    Returns
    -------
    dict
        [description]

    Raises
    ------
    Exception
        [description]
    """
    # Инициализирует вещества указанные в yaml файле
    # Возвращает список объектов Compound

    _list_with_compound_objects = []

    if list_with_compounds:
        pass
    else:
        # TODO Исключение
        raise Exception('compounds_init()')

    for compounds in list_with_compounds:
        _list_with_compound_objects.append(Compound.from_dict(compounds))

    return {
        compound.name: compound
        for compound in _list_with_compound_objects
    }


def chemical_equation_pars(reaction: str = None) -> Tuple:
    """[summary]

    Parameters
    ----------
    reaction : str, optional
        [description], by default None

    Returns
    -------
    tuple
        [description]

    Raises
    ------
    Exception
        [description]
    """
    # Инициализирует продукты и реагенты указанные в реакции
    # Возвращает список из двух словарей с продуктами и реагентами
    # и коэффициентом для каждого в-ва

    if reaction and len(reaction.split('=')) == 2:
        pass
    else:
        # TODO Исключение
        raise Exception('reaction_init()')

    # element[0] - reagents, elements[1] - products

    dict_repr_reaction = []
    for element in reaction.split('='):
        semi_reaction = {}
        for compound in element.split('+'):
            if '*' in compound:
                # compound looks like '2*S'
                coefficient = compound.split('*')[0].strip()
                compound_name = compound.split('*')[1].strip()
                semi_reaction[compound_name] = coefficient
            else:
                # S
                semi_reaction[compound.strip()] = 1
        dict_repr_reaction.append(semi_reaction)

    # где dict_repr_reaction[0] - словарь {имя в-ва: коэффициент} c реагентами
    # dict_repr_reaction[1] - аналогичный словарь для продуктов р-ции
    return tuple(dict_repr_reaction)
