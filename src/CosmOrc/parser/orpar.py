# %%
__author__ = 'Anton Domnin, Yaroslav Solovev'
__license__ = 'GPL3'
__maintainer__ = 'Anton Domnin'
__email__ = 'a.v.daomnin@gmail.com, yaroslavsolovev78@gmail.com'


import pandas as pd
import re
from src.CosmOrc.basic.setting import Setting

parameter_list = ('Electronic energy',
                  'Zero point energy',
                  'Thermal vibrational correction',
                  'Thermal rotational correction',
                  'Thermal translational correction',
                  'Thermal Enthalpy correction',
                  'Vibrational entropy',
                  'Rotational entropy',
                  'Total Mass',
                  'Translational entropy',
                  'Temperature',
                  'Pressure',
                  'T*S(rot)',
                  'cm**-1',
                  'THERMOCHEMISTRY')


def read_data_orca(file_path=None):
    """Функция считывает из файла строки, в которые входят элементы
    из parameter_list, и добавляет их в список matching.
    Возвращает список только в том случае, если слово
    'THERMOCHEMISTRY' есть в этом списке. Наличие 'THERMOCHEMISTRY'
    автоматически  гарантирует наличие термодинамических данных в файле

    Arguments
    ---------
    file_path: str
        Путь к файлу для парсинга

    Return
    ------
    matching: list
        Список со строками, в которые входят строки из
        списка parameter_list
    """
    matching = []
    with open(file_path, "r") as data_file:
        for line in data_file:
            if any(xs in line for xs in parameter_list):
                matching.append(line)
    if any('THERMOCHEMISTRY' in s for s in matching):
        return matching


def tsrot_pars(some_string: str):
    """Функция необходима для парсинга строк в которые входит TSrot
    (вращательная энтропия умноженная на температуру), на вход
    принимает строку в которой параметры указаны в kcal/mol,
    а возвращает объект класса Setting переконвертировав в J/mol.

    Arguments
    ---------
    some_string: str
        Строка содержащая в себе значение вращательной энтропии 

    Return
    ------
        Возвращает объект класса Setting, содержащий в себе
        значения TSrot в J/mol.
    """
    _sn_coef_ = r'sn=\s?([\d.]+)'
    _some_info_ = r'[\s]+qrot.sn=[\s]+[-\d.]+\s'
    _TSrot_segment_ = r'T\*S\(rot\)=[\s]+'
    _value_ = r'([-\d.]+)[\s]+kcal\/mol'
    _reg = re.search(_sn_coef_ + _some_info_ +
                     _TSrot_segment_ + _value_,
                     some_string)
    if _reg:
        _sn_coef = _reg.group(1)
        _value = _reg.group(2)
        _unit = 'kcal/mol'
        return Setting(name=f'{_sn_coef} T*S(rot)',
                       value=_value,
                       unit=_unit).convert(koef=4182, unit='J/mol')


def tp_pars(some_string: str):
    """Функция для парсинга строк содержащих значения температуры и давления

    Arguments
    ---------
    some_string: str
        Строка содержащая в себе значение параметра
        (температура или давление)

    Return
    ------
        Возвращает объект класса Setting, содержащий в себе
        значения параметра в J/mol.
    """
    _name_ = r'([\w\s]+)'
    _dots_ = r'\s*\.\.\.\s*'
    _value_ = r'([\d]+.[\d]+)'
    _unit_ = r'\s*(\w+)'

    _reg = re.search(_name_ + _dots_ +
                     _value_ + _unit_,
                     some_string)
    if _reg:
        return Setting(name=_reg.group(1).split()[0],
                       value=_reg.group(2),
                       unit=_reg.group(3))


def other_param_pars(some_string: str):
    """Функция предназначена для парсинга параметров, указанных в Eh,
    автоматически конвертирует их в J/mol

    Arguments
    ---------
    some_string: str
        Строка содержащая в себе значения вращательной энтропии

    Return
    ------
        Возвращает объект класса Setting, содержащий в себе
        значения параметра в J/mol.
    """
    _name_ = r'([\w\s]+\w+)'
    _dots_ = r'\s*\.\.\.\s*'
    _value_ = r'([-\d.]+)\s*.*'
    _reg = re.search(_name_ + _dots_ + _value_, some_string)

    if _reg:
        return Setting(name=_reg.group(1),
                       value=_reg.group(2),
                       unit='Eh').convert(koef=2625500, unit='J/mol')


def freq_pars(some_str: str):
    """Функция для парсинга строк содержащих значения частот

    Arguments
    ---------
    some_string: str
        Строка содержащая в себе значение частоты

    Return
    ------
        Возвращает объект класса Setting, содержащий в себе
        значения параметра в cm**-1.
    """
    _freq_number_ = r'([\d]+):\s+'
    _value_ = r'([-\d.]+)'
    _unit_ = r'\s(cm\**-1)'
    _reg = re.search(_freq_number_ + _value_ + _unit_, some_str)

    if _reg:
        return Setting(name='freq.',
                       value=_reg.group(2),
                       unit=_reg.group(3))


def pars_all_matches(data: list or tuple):
    """Функция объединяет в себе все предыдущие функции,
    на вход получает набор готовых данных из read_data_orca,
    а возвращает объект pd.Series, содержащий в себе все данные из
    указанного файла.

    Arguments
    ---------
    data: list or tuple
        Список, возвращаемый функцией read_data_orca

    Return
    ------
        Объект pd.Serires (pd == pandas), содержаший в себе
        данные из исходного файла.
    """
    _all_settings = []
    if data:
        for string in reversed(data):
            if 'sn=' in string:
                _all_settings.append(tsrot_pars(string))
            elif 'Temperature' in string:
                _all_settings.append(tp_pars(string))
            elif 'Pressure' in string:
                _all_settings.append(tp_pars(string))
            elif 'Total Mass' in string:
                _all_settings.append(tp_pars(string))
            elif 'cm**-1' in string:
                _all_settings.append(freq_pars(string))
            else:
                _all_settings.append(other_param_pars(string))
    return pd.Series(data=_all_settings).dropna()


def main():
    pass


if __name__ == '__main__':
    main()
