import os
import re

import argparse as ag
import pandas as pd

from src.CosmOrc.basic.setting import Setting

EhToJ_Mol = 4.359744 * 6.022e5

parameter_list = [
    'Zero-point correction', 'Thermal correction to Energy',
    'Thermal correction to Enthalpy',
    'Thermal correction to Gibbs Free Energy',
    'Sum of electronic and zero-point Energies',
    'Sum of electronic and thermal Energies',
    'Sum of electronic and thermal Enthalpies',
    'Sum of electronic and thermal Free Energies'
]

properties_list = [
    'Total', 'Electronic', 'Translational', 'Rotational', 'Vibrational'
]


def list_unapck(some_list: list or tuple = None) -> tuple:
    """Функция для распаковки списков. Распаковывает вложенные
    списки на один уровень.

    Arguments
    ---------
    some_list: list or tuple
        Список содержащий вложенные списки

    Return
    ------
    new_list: tuple
        Список, распкованный на один уровень
    """
    new_list = []
    for element in some_list:
        if isinstance(element, (list, tuple)):
            for i in element:
                new_list.append(i)
        else:
            new_list.append(element)
    return tuple(new_list)


# TODO Убрать и протестировать сколько будет занимать по времени
def read_data_gaussian(file_path: str = None) -> tuple:
    # TODO Переделать с учетом того что file_path = None
    """Функция для чтения данных из Gaussian. Проверяет есть ли
    термохимические данные в файле, и считывает нужные строки

    Arguments
    ---------
    file_path: str
        Путь к *.out файлу Gaussian

    Return
    ------
    matching: tuple
        Кортеж в который входят все строки содержащие в себе
        элементы списков parameter_list или properties_list
    """
    matching = []
    scf_energy = None
    with open(file_path, 'r') as data_file:
        for line in data_file:
            if any(
                    xs in line for xs in (
                        parameter_list + properties_list +
                        ['Frequencies', 'Temperature', 'Molecular mass'])):
                matching.append(line)
            if 'SCF Done' in line:
                scf_energy = line
        matching.append(scf_energy)
    return tuple(matching)


# TODO Сделать парсер для давлений и температуры
# (Temperature)\s*([0-9.]+)\s*([\w]+).\s*(Pressure)\s*([0-9.]+)\s*([\w]+).


def scf_energy_pars(some_str: str = None):
    _scf_energy = r'SCF\sDone:\s*E[\w\d()-]*\s*=\s*([-\d.]*)'
    _scf_energy_string = re.search(_scf_energy, some_str)
    if _scf_energy_string:
        return Setting(
            name='SCF Energy', value=_scf_energy_string.group(1),
            unit='Eh').convert(
                koef=EhToJ_Mol, unit='J/mol')


def molecular_mass_pars(some_str: str = None) -> Setting:
    # TODO Написать документацию и переделать с учетом того что строка = None
    """Парсер молеколуярной массы
    """
    _mol_mass = r'Molecular mass:\s*([0-9.]+)\s*([\w]+).'
    _mol_mass_string = re.search(_mol_mass, some_str)
    if _mol_mass_string:
        return Setting(
            name='Molecular mass',
            value=_mol_mass_string.group(1),
            unit=_mol_mass_string.group(2))


def tp_pars(some_str: str = None) -> list:
    """Функция для парсинга температуры и давленя в *.out файле

    Arguments
    ---------
    some_str: str

    Return
    ------
    Список содержащий два объекта класса Setting,
    Температура и давление соответсвенно
    """
    _temperature = r'(Temperature)\s*([0-9.]+)\s*([\w]+).'
    _pressure = r'(Pressure)\s*([0-9.]+)\s*([\w]+).'
    tp_string = re.search(_temperature + r'\s*' + _pressure, some_str)
    if tp_string:
        return [
            Setting(
                name=tp_string.group(1),
                value=tp_string.group(2),
                unit=tp_string.group(3)),
            Setting(
                name=tp_string.group(4),
                value=tp_string.group(5),
                unit=tp_string.group(6))
        ]


def freq_pars(some_str: str = None) -> list:
    # TODO Переделать с учетом того что str = None
    """Функция для парсинга частот

    Arguments
    ---------
    some_string: str
        Строка содержащая в себе значение частоты

    Return
    ------
        Возвращает список содержащий в себе объекты класса Setting,
        с значениями частот в cm**-1.
    """
    _current_freq_ = []
    _name_ = r'(\w+)'
    _freq_value_ = r'([-\d.]+)'
    freq_str = re.search(
        _name_ + r'\s\-\-\s*' + _freq_value_ + r'\s*' + _freq_value_ + r'\s*' +
        _freq_value_, some_str)
    if freq_str:
        for i in range(2, 5):
            _current_freq_.append(
                Setting(name='freq.', value=freq_str.group(i), unit='cm**-1'))
    return _current_freq_


def parameter_pars(some_str: str = None) -> Setting:
    # TODO Переделать с учетом того что some_str = None
    """Функция для парсинга термодинамических параметров, должна
    принимать строки содержащие в себе один элемент из списка
    parameter_list

    Arguments
    ---------
    some_str: str
        Строка для парсинга

    Return
    ------
    Возвращает объект класса Setting, содержащий в себе термодинамические
    парамаетры в J/mol
    """
    _name_ = some_str.split('=')[0]
    _value_ = r'(-?[0-9]{1,10}\.[0-9]{6})'
    param_str = re.search(_value_, some_str)
    # koef = 4.359744 * 6.022e5
    # hartree_to_yj_coef / N_Avogadro
    if param_str:
        return Setting(
            name=_name_[1:], value=param_str.group(1), unit='Eh').convert(
                koef=EhToJ_Mol, unit='J/mol')


def properties_pars(some_str: str = None) -> Setting:
    # TODO Дописать документацию
    # TODO Переделать с учетом того что file_path = None
    """Функция для прасинга энтропии, принимает строку содежащую
    одно из слов списка properties_list, возращает объект класса Setting
    в J/mol*K

    Arguments
    ---------
    some_str: str


    Return
    ------

    """
    _name_ = some_str.split()[0]
    _value_ = r'([0-9]{1,10}\.[0-9]{3})'
    _whitespace_ = r'\s{2,15}'
    entropy_str = re.search(
        _value_ + _whitespace_ + _value_ + _whitespace_ + _value_, some_str)
    if entropy_str:
        return Setting(
            name=_name_ + ' Entropy',
            value=entropy_str.group(3),
            unit='Cal/mol*K').convert(
                koef=4.184, unit='J/mol*K')


def file_pars(file_path: str = None) -> pd.Series:
    # TODO Дописать документацию. Функция в целом нуждается в доработке
    """
    """
    read_data = read_data_gaussian(file_path)
    _all_setting = []
    if read_data:
        for line in read_data:
            if 'Frequencies' in line:
                _all_setting.append(freq_pars(line))
            elif any(xs in line for xs in parameter_list):
                _all_setting.append(parameter_pars(line))
            elif any(xs in line for xs in properties_list):
                _all_setting.append(properties_pars(line))
            elif 'Temperature' in line:
                _all_setting.append(tp_pars(line))
            elif 'Molecular mass' in line:
                _all_setting.append(molecular_mass_pars(line))
            elif 'SCF Done' in line:
                _all_setting.append(scf_energy_pars(line))
            else:
                pass

    raw_data = list_unapck(_all_setting)
    data = [parameter for parameter in raw_data if parameter is not None]
    if data:
        indexes = [parameter.name for parameter in data]
        return pd.Series(
            data=[x.value for x in data], name='parameters', index=indexes)
