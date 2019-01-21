# %%
import re
import pandas as pd
from src.CosmOrc.basic.setting import Setting


parameter_list = ['Zero-point correction',
                  'Thermal correction to Energy',
                  'Thermal correction to Enthalpy',
                  'Thermal correction to Gibbs Free Energy',
                  'Sum of electronic and zero-point Energies',
                  'Sum of electronic and thermal Energies',
                  'Sum of electronic and thermal Enthalpies',
                  'Sum of electronic and thermal Free Energies']

properties_list = ['Total',
                   'Electronic',
                   'Translational',
                   'Rotational',
                   'Vibrational']


def list_unapck(some_list: list or tuple):
    """Функция для распаковки списков. Распаковывает вложенные
    списки на один уровень.

    Arguments
    ---------
    some_list: list or tuple
        Список содержащий вложенные списки

    Return
    ------
    new_list: list
        Список, распкованный на один уровень
    """
    new_list = []
    for element in some_list:
        if isinstance(element, (list, tuple)):
            for i in element:
                new_list.append(i)
        else:
            new_list.append(element)
    return new_list


def read_data_gaussian(file_path: str):
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
    with open(file_path, 'r') as data_file:
        for line in data_file:
            if any(xs in line for xs in (parameter_list +
                   properties_list + ['Frequencies', 'Temperature'])):
                matching.append(line)
    return tuple(matching)


# TODO Сделать парсер для давлений и температуры
# (Temperature)\s*([0-9.]+)\s*([\w]+).\s*(Pressure)\s*([0-9.]+)\s*([\w]+).

def tp_pars(some_str: str):
    """Функция для парсинга температуры и давленя в *.out файле

    Arguments
    ---------
    some_str: str

    Return
    ------
    Объект класса Setting
    """
    _temperature = r'(Temperature)\s*([0-9.]+)\s*([\w]+).'
    _pressure = r'(Pressure)\s*([0-9.]+)\s*([\w]+).'
    tp_string = re.search(_temperature + r'\s*' + _pressure, some_str)
    if tp_string:
        return [Setting(name=tp_string.group(1),
                        value=tp_string.group(2),
                        unit=tp_string.group(3)),
                Setting(name=tp_string.group(4),
                        value=tp_string.group(5),
                        unit=tp_string.group(6))]


def freq_pars(some_str: str):
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
    freq_str = re.search(_name_ + r'\s\-\-\s*' + _freq_value_ + r'\s*'
                         + _freq_value_ + r'\s*' + _freq_value_, some_str)
    if freq_str:
        for i in range(2, 5):
            _current_freq_.append(Setting(name='freq.',
                                          value=freq_str.group(i),
                                          unit='cm**-1'))
    return _current_freq_


def parameter_pars(some_str: str):
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
    if param_str:
        return Setting(name=_name_[1:],
                       value=param_str.group(1),
                       unit='Eh').convert(koef=2625500, unit='J/mol')


def properties_pars(some_str: str):
    # TODO Дописать документацию
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
    entropy_str = re.search(_value_ + _whitespace_ + _value_
                            + _whitespace_ + _value_, some_str)
    if entropy_str:
        return Setting(name=_name_ + ' Entropy',
                       value=entropy_str.group(3),
                       unit='Cal/mol*K').convert(koef=4.184, unit='J/mol*K')


def file_pars(file_path: str):
    # TODO Дописать документацию
    """
    """
    data = read_data_gaussian(file_path)
    _all_setting = []
    if data:
        for line in data:
            if 'Frequencies' in line:
                _all_setting.append(freq_pars(line))
            elif any(xs in line for xs in parameter_list):
                _all_setting.append(parameter_pars(line))
            elif any(xs in line for xs in properties_list):
                _all_setting.append(properties_pars(line))
            elif 'Temperature' in line:
                _all_setting.append(tp_pars(line))
            else:
                pass
    return pd.Series(list_unapck(_all_setting)).dropna()


def main():
    pass


if __name__ == '__main__':
    main()