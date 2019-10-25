import os
import re
from typing import Any, List, Tuple, Union

import pandas as pd

from utils.setting import Setting


EH_JMOL = 4.359744 * 6.022e5

PARAMETER_LIST = [
    'Zero-point correction', 'Thermal correction to Energy',
    'Thermal correction to Enthalpy',
    'Thermal correction to Gibbs Free Energy',
    'Sum of electronic and zero-point Energies',
    'Sum of electronic and thermal Energies',
    'Sum of electronic and thermal Enthalpies',
    'Sum of electronic and thermal Free Energies'
]

PROPERTIES_LIST = [
    'Total', 'Electronic', 'Translational', 'Rotational', 'Vibrational'
]


# ^\s+(\d+)\s+\d+\s+\d+\s+\-?[\d.]+\s+\-?[\d.]+\s+\-?[\d.]+$ для атомов

def list_unpack(some_list: Union[List, Tuple]) -> List:
    """
    Функция для распаковки списков. Распаковывает вложенные
    списки на один уровень.

    Parameters
    ----------
    some_list: list or Tuple
        Список c уровнем вложенности равным n

    Return
    ------
    new_list: Tuple
        Список,с уровнем вложенности n - 1; n - 1 >= 1

    Example
    -------
    >>> some_list = [1, 2, [3, 4], [5, [6]]]
    >>> list_unpack(some_list)
    (1, 2, 3, 4, 5, [6])
    """
    new_list = []
    for element in some_list:
        if isinstance(element, (list, tuple)):
            for i in element:
                new_list.append(i)
        else:
            new_list.append(element)
    return new_list


def read_data_gaussian(file_path: Union[str, 'os.PathLike[Any]']) -> List:
    """
    Функция для чтения данных из Gaussian. Проверяет есть ли
    термохимические данные в файле, и считывает нужные строки

    Parameters
    ---------
    file_path: str, 'os.PathLike[Any]'
        Путь к *.out файлу Gaussian

    Returns
    ------
    matching: Tuple
        Кортеж в который входят все строки содержащие в себе
        элементы списков PARAMETER_LIST или PROPERTIES_LIST

    Raises
    ------
    UnboundLocalError
        Возникает при отсутствие "обязательных строк", строки содержат общую
        информацию о структуре, поэтому их отсутствие является ошибкой
    """
    matching: List[str] = []
    scf_energy: str
    with open(file_path, 'r') as data_file:
        for line in data_file:
            if any(
                    xs in line for xs in (
                        PARAMETER_LIST + PROPERTIES_LIST +
                        ['Frequencies', 'Temperature', 'Molecular mass'])):
                matching.append(line)
            # Нужно только последнее значение для каждой из строк
            # Эти строки должны встречаться в любом файле Gaussian
            # Поэтому их отсутствие является ошибкой
            if 'SCF Done' in line:
                scf_energy = line
            if 'NAtoms' in line:
                d_line = line
            if 'Full point group' in line:
                sym_line = line
            if 'Deg. of freedom' in line:
                free_line = line
        try:
            matching.append(free_line)
            matching.append(sym_line)
            matching.append(d_line)
            matching.append(scf_energy)
        except UnboundLocalError as err:
            raise err
        except Exception as err:
            raise err
    return matching


def scf_energy_pars(some_str: str):
    """
    Функция для извлечения электронной энергии

    Parameters
    ----------
    some_str : str
        Строка для парсинга

    Returns
    -------
    Setting
        Содержит название, значение и единицы измерения параметра
    """
    _scf_energy = r'SCF\sDone:\s*E[\w\d()-]*\s*=\s*([-\d.]*)'
    _scf_energy_string = re.search(_scf_energy, some_str)
    if _scf_energy_string:
        return Setting(
            name='scf energy', value=_scf_energy_string.group(1),
            unit='Eh').convert(
                koef=EH_JMOL, unit='J/mol')


def molecular_mass_pars(some_str: str) -> Setting:
    """
    Функция для извлечения молекулярной массы

    Parameters
    ----------
    some_str : str
        Строка для парсинга

    Returns
    -------
    Setting
        Содержит название, значение и единицы измерения параметра
    """
    _mol_mass = r'Molecular mass:\s*([0-9.]+)\s*([\w]+).'
    _mol_mass_string = re.search(_mol_mass, some_str)
    if _mol_mass_string:
        return Setting(
            name='Molecular mass',
            value=_mol_mass_string.group(1),
            unit=_mol_mass_string.group(2))


def tp_pars(some_str: str) -> List:
    """
    Функция для парсинга температуры и давленя в *.out файле

    Parameters
    ---------
    some_str: str

    Returns
    ------
    Список содержащий два объекта класса Setting,
    Температура и давление соответственно
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


def freq_pars(some_str: str) -> list:
    """
    Функция для парсинга частот

    Parameters
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
    _reg_str = _name_ + r'\s\-\-\s*'
    # Когда в строке не 3 частоты
    # Мы можем учесть это размером регулярного выражения
    for i in range(len(some_str.split()) - 2):
        _reg_str += _freq_value_ + r'\s*'
    freq_str = re.search(_reg_str, some_str)
    if freq_str:
        for i in range(2, len(some_str.split())):
            _current_freq_.append(
                Setting(name='freq.', value=freq_str.group(i), unit='cm**-1'))
    return _current_freq_


def parameter_pars(some_str: str) -> Setting:
    """Функция для парсинга термодинамических параметров, должна
    принимать строки содержащие в себе один элемент из списка
    PARAMETER_LIST

    Parameters
    ---------
    some_str: str
        Строка для парсинга

    Return
    ------
    Возвращает объект класса Setting, содержащий в себе термодинамические
    параметры в J/mol
    """
    _name_ = some_str.split('=')[0]
    _value_ = r'(-?[0-9]{1,10}\.[0-9]{6})'
    param_str = re.search(_value_, some_str)
    # coef = 4.359744 * 6.022e5
    # hartree_to_j_coef / N_Avogadro
    if param_str:
        return Setting(
            name=_name_[1:], value=param_str.group(1), unit='Eh').convert(
                koef=EH_JMOL, unit='J/mol')


def properties_pars(some_str: str) -> Setting:
    """
    Извлекает значение и название типа энтропии из строки

    Parameters
    ----------
    some_str : str
        Строки типа: "Vibrational 120.478 27.641 25.420"

    Returns
    -------
    Setting
        Содержит название, значение в J/Mol*K, и единицы измерения
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


def file_pars(file_path: str) -> pd.Series:
    """
    Принимает на вход путь к файлу, и парсит его, возвращая результаты в виде
    pandas.Series, если в файле не было данных или нужного файла не существует
    вылетит с ошибкой.

    Parameters
    ----------
    file_path : str
        Путь к файлу *.out

    Returns
    -------
    pd.Series
        Серия содержит термохимические и структурные параметры,
        необходимые для дальнейшего получения термодинамических данных
    """
    read_data = read_data_gaussian(file_path)
    _all_parameters = []
    if read_data:
        for line in read_data:
            if 'Frequencies' in line:
                _all_parameters.append(freq_pars(line))
            elif any(xs in line for xs in PARAMETER_LIST):
                _all_parameters.append(parameter_pars(line))
            elif any(xs in line for xs in PROPERTIES_LIST):
                _all_parameters.append(properties_pars(line))
            elif 'Temperature' in line:
                _all_parameters.append(tp_pars(line))
            elif 'Molecular mass' in line:
                _all_parameters.append(molecular_mass_pars(line))
            elif 'SCF Done' in line:
                _all_parameters.append(scf_energy_pars(line))
            elif 'NAtoms' in line:
                _all_parameters.append(
                    Setting(name='natoms', value=line.split()[1], unit='n'))
            elif 'Full point group' in line:
                sym_line = line.split()[3]
                _all_parameters.append(
                    Setting(name=line.split()[4], value=line.split()[5], unit=''))
            elif 'Deg. of freedom' in line:
                _all_parameters.append(
                    Setting(name='deg. of freedom', value=line.split()[3], unit=''))
            else:
                pass

    raw_data = list_unpack(_all_parameters)
    data = [parameter for parameter in raw_data if parameter is not None]
    # TODO Comments
    if data:
        indexes = [parameter.name for parameter in data]
        series = pd.Series(data=[x.value for x in data],
                           name='parameters', index=indexes)
        series.loc['full point group'] = sym_line
        series.loc['qm_program'] = 'gaussian'
        if series.loc['natoms'] == 1:
            series.loc['atom'] = True
            series.loc['linear'] = True
        else:
            series.loc['atom'] = False
            if series.loc['deg. of freedom'] == 1:
                series.loc['linear'] = True
            elif series.loc['natoms'] > 1 and series.loc['natoms']*3 - 5 == len(series.loc['freq.']):
                series.loc['linear'] = True
            else:
                series.loc['linear'] = False
        return series
    # TODO Fixme
