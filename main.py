import os
import yaml
import glob
import argparse as ag

import numpy as np
import pandas as pd

from typing import List, Set, Dict, Tuple, Any
from typing import Callable, Iterable, Union, Optional, List

from src.CosmOrc.basic._basic import profile, timeit
from src.CosmOrc.basic.thermochemistry import Reaction, Compound



def chemical_equation_pars(reaction: str, compound_dict: Dict[str, Compound]) -> Tuple[Dict[str, Tuple[float, Compound]], ...]:
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
    # TODO ИМЕНА ПЕРЕМЕННЫХ!!!!
    dict_repr_reaction = []
    for element in reaction.split('='):
        semi_reaction = {}
        for compound in element.split('+'):
            if '*' in compound:
                # compound looks like '2*S'
                coefficient = float(compound.split('*')[0].strip())
                compound_name = compound.split('*')[1].strip()
                semi_reaction[compound_name] = (
                    coefficient, compound_dict[compound_name])
            else:
                # S
                semi_reaction[compound.strip()] = (
                    1, compound_dict[compound_name])
        dict_repr_reaction.append(semi_reaction)
    # где dict_repr_reaction[0] - словарь {имя в-ва: коэффициент} c реагентами
    # dict_repr_reaction[1] - аналогичный словарь для продуктов р-ции

    return tuple(dict_repr_reaction)


def compounds_init(list_with_compounds: List[Dict[str, str]]) -> Dict[str, Compound]:
    """
    Инициализирует все вещества из списка,

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
