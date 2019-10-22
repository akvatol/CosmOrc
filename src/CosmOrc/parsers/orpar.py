# __author__ = 'Anton Domnin, Yaroslav Solovev'
# __license__ = 'GPL3'
# __maintainer__ = 'Anton Domnin'
# __email__ = 'a.v.daomnin@gmail.com, yaroslavsolovev78@gmail.com'

import re
from typing import Any, List, Tuple, Union

import pandas as pd

from src.CosmOrc.basic.setting import Setting

EH_JMOL = 4.359744 * 6.022e5


PARAMETER_LIST = ('Electronic energy', 'Zero point energy',
                  'Thermal vibrational correction',
                  'Thermal rotational correction',
                  'Thermal translational correction',
                  'Thermal Enthalpy correction', 'Vibrational entropy',
                  'Rotational entropy', 'Total Mass', 'Translational entropy',
                  'Temperature', 'Pressure', 'T*S(rot)', 'cm**-1', 'Electronic entropy',
                  'THERMOCHEMISTRY', 'Total enthalpy', 'Final Gibbs free enthalpy')


def read_data_orca(file_path: str = None):
    """
    Функция считывает из файла строки, в которые входят элементы
    из PARAMETER_LIST, и добавляет их в список matching.
    Возвращает список только в том случае, если слово
    'THERMOCHEMISTRY' есть в этом списке. Наличие 'THERMOCHEMISTRY'
    автоматически  гарантирует наличие термодинамических данных в файле

    Parameters
    ---------
    file_path: str
        Путь к файлу для парсинга

    Returns
    ------
    matching: list
        Список со строками, в которые входят строки из
        списка PARAMETER_LIST
    """

    matching = []
    with open(file_path, "r") as data_file:
        for line in data_file:
            if any(xs in line for xs in PARAMETER_LIST):
                matching.append(line)
            if 'Number of atoms' in line:
                atm_line = line
            if 'Number of degrees of freedom' in line:
                deg_line = line
    if any('THERMOCHEMISTRY' in s for s in matching):
        try:
            matching.append(atm_line)
            matching.append(deg_line)
        except UnboundLocalError as err:
            # logging.error(traceback.format_exc())
            raise err
        except Exception as err:
            # logging.error('unexpected error while {file_path} reading')
            # logging.error(traceback.format_exc())
            raise err
        return matching


def tsrot_pars(some_string: str):
    """Функция необходима для парсинга строк в которые входит TSrot
    (вращательная энтропия умноженная на температуру), на вход
    принимает строку в которой параметры указаны в kcal/mol,
    а возвращает объект класса Setting переконвертировав в J/mol.

    Parameters
    ---------
    some_string: str
        Строка содержащая в себе значение вращательной энтропии

    Returns
    ------
        Возвращает объект класса Setting, содержащий в себе
        значения TSrot в J/mol.
    """
    _sn_coef_ = r'sn=\s?([\d.]+)'
    _some_info_ = r'[\s]+qrot.sn=[\s]+[-\d.]+\s'
    _tsrot_segment_ = r'T\*S\(rot\)=[\s]+'
    _value_ = r'([-\d.]+)[\s]+kcal\/mol'
    _reg = re.search(_sn_coef_ + _some_info_ + _tsrot_segment_ + _value_,
                     some_string)
    if _reg:
        _sn_coef = _reg.group(1)
        _value = _reg.group(2)
        _unit = 'kcal/mol'
        return Setting(
            name=f'{_sn_coef} T*S(rot)', value=_value, unit=_unit).convert(
                koef=4184, unit='J/mol')


def tp_pars(some_string: str):
    """Функция для парсинга строк содержащих значения температуры и давления

    Parameters
    ---------
    some_string: str
        Строка содержащая в себе значение параметра
        (температура или давление)

    Returns
    ------
        Возвращает объект класса Setting, содержащий в себе
        значения параметра в J/mol.
    """
    _name_ = r'([\w\s]+)'
    _dots_ = r'\s*[\.]+\s*'
    _value_ = r'([\d]+.[\d]+)'
    _unit_ = r'\s*(\w+)'

    _reg = re.search(_name_ + _dots_ + _value_ + _unit_, some_string)
    if _reg:
        return Setting(
            name=_reg.group(1).split()[0],
            value=_reg.group(2),
            unit=_reg.group(3))


def other_param_pars(some_string: str):
    """Функция предназначена для парсинга параметров, указанных в Eh,
    автоматически конвертирует их в J/mol

    Parameters
    ---------
    some_string: str
        Строка содержащая в себе значения вращательной энтропии

    Returns
    ------
        Возвращает объект класса Setting, содержащий в себе
        значения параметра в J/mol.
    """
    _name_ = r'([\w\s]+\w+)'
    _dots_ = r'\s*[\.]+\s*'
    _value_ = r'([-\d.]+)\s*.*'
    _reg = re.search(_name_ + _dots_ + _value_, some_string)

    if _reg:
        return Setting(
            name=_reg.group(1), value=_reg.group(2), unit='Eh').convert(
                koef=EH_JMOL, unit='J/mol')


def freq_pars(some_str: str):
    """Функция для парсинга строк содержащих значения частот

    Parameters
    ---------
    some_string: str
        Строка содержащая в себе значение частоты

    Returns
    ------
        Возвращает объект класса Setting, содержащий в себе
        значения параметра в cm**-1.
    """
    _freq_number_ = r'([\d]+):\s+'
    _value_ = r'([-\d.]+)'
    _unit_ = r'\s(cm\**-1)'
    _reg = re.search(_freq_number_ + _value_ + _unit_, some_str)

    if _reg:
        return Setting(name='freq.', value=_reg.group(2), unit=_reg.group(3))


def name_value_pars(some_str: str):
    _name = r'([\w\s]+)'
    _dots = r'\s*[\.]+\s*'
    _value = r'([\d]+)'
    _reg = re.search(_name + _dots + _value, some_str)

    if _reg:
        return Setting(name=_reg.group(1), value=_reg.group(2), unit='')


def post_process(element: Setting):

    if element.name == 'number of atoms':
        element.convert(name='natoms')
    elif element.name == 'total':
        element.convert(name='molecular mass')
    elif element.name == 'zero point energy':
        element.convert(name='zero-point energy')
    elif element.name == 'final gibbs free enthalpy':
        element.convert('sum of electronic and thermal free energies')
    elif element.name == 'total enthalpy':
        element.convert(name='sum of electronic and thermal enthalpies')
    elif element.name == 'electronic energy':
        element.convert(name='scf energy')
    elif 'thermochemistry at' in element.name:
        element = None
    elif element.name == 'number of degrees of freedom':
        element.convert('deg. of freedom')
    elif element.name == 'freq.' and element.value == 0:
        element = None
    else:
        pass
    return element


def file_pars(file_path: str = None):
    """Функция объединяет в себе все предыдущие функции,
    на вход получает набор готовых данных из read_data_orca,
    а возвращает объект pd.Series, содержащий в себе все данные из
    указанного файла.

    Parameters
    ---------
    data: list or tuple
        Список, возвращаемый функцией read_data_orca

    Return
    ------
        Объект pd.Serires (pd == pandas), содержащий в себе
        данные из исходного файла.
    """
    read_data = read_data_orca(file_path)
    _all_parameters = []
    if read_data:
        for string in reversed(read_data):
            if 'sn=' in string:
                _all_parameters.append(tsrot_pars(string))
            elif 'Temperature' in string:
                _t = tp_pars(string)
                _all_parameters.append(tp_pars(string))
            elif 'Pressure' in string:
                _all_parameters.append(tp_pars(string))
            elif 'Total Mass' in string:
                _all_parameters.append(tp_pars(string))
            elif 'cm**-1' in string:
                if freq_pars(string) != 0:
                    _all_parameters.append(freq_pars(string))
            elif 'Number of atoms' in string:
                _all_parameters.append(name_value_pars(string))
            elif 'Number of degrees of freedom' in string:
                _all_parameters.append(name_value_pars(string))
            else:
                _all_parameters.append(other_param_pars(string))

    raw_data = [post_process(element)
                for element in _all_parameters if element is not None]

    # Because in orca entropy is T*S
    for element in raw_data:
        if element and 'entropy' in element.name:
            element.convert(koef=_t.value**(-1))
        elif element and 't*s' in element.name:
            # change name and value from "x t*s(rot)" to "x s(rot)"
            new_name = element.name.split()[0] + ' s(rot)'
            element.convert(koef=_t.value**(-1), name=new_name)

    data = [parameter for parameter in raw_data if parameter is not None]

    if data:
        indexes = [parameter.name for parameter in data]
        series = pd.Series(data=[x.value for x in data],
                           name='parameters', index=indexes)
        series.loc['qm_program'] = 'orca'
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

    return pd.Series(data=_all_parameters)


def main():
    pass


if __name__ == '__main__':
    main()
