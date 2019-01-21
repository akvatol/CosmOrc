# %%
import pandas as pd
from src.CosmOrc.basic.setting import Setting


def chunkit(data: list or tuple, n=None):
    """
    Функция разбивает исходный массив на N частей (N == n).

    Arguments
    ---------
    data_list: list or tuple
        Массив, который будет разделен на n частей
    n: int
        Число подмассивов в возвращаемом массиве (default: 2)

    Returns
    -------
    list: разделенный на части список

    Example
    -------
    >>> l = [1, 2, 3, 4, 5, 6, 7, 8]
    >>> a = chunkit(l)
    >>> print(a)
    [[1, 2, 3, 4], [5, 6, 7, 8]]
    >>> b = chunkit(l, n=4)
    >>> print(b)
    [[1, 2], [3, 4], [5, 6], [7, 8]]
    """
    new_data = []
    if not n:
        n = 2
    avg = len(data) / n
    last = 0
    while last < len(data):
        new_data.append(data[int(last):int(last + avg)])
        last += avg
    return new_data


def read_data_cosmo(file_path: str):
    with open(file_path, 'r') as file:
        data = []
        for line in file:
            if line.split():
                if 'Setting' in line:
                    jobs_data = []
                    jobs_data.append(line)
                    data.append(jobs_data)
                elif 'job' not in line or 'Units' in line:
                    jobs_data.append(line)
                else:
                    pass
    return data


def setting_pars(settings_str: str):
    """Функция для извлечения параметров расчета из строк,
    принимает строку из *.tab файла, содержащую подстроку
    'Settings'

    Arguments
    ---------
    settings_str: str
        Строка *.tab файла, содержащая ключевое слово 'Settings'

    Return
    ------
    settings_list: tuple
        Кортеж содержащий объекты класса Setting, описывающие
        условия проведения расчета

    Example
    -------
    >>> setting_pars('Settings  job 2 : T= 223.15 K ; x(1)= 0.1000;')
    (T= 223.15 K, x(1)= 0.1 %)
    """
    settings_list = []
    new_line = settings_str.split(':')[1]
    settings = new_line.split(';')
    for setting in settings:
        if len(setting.split()) == 3:
            settings_list.append(Setting.from_record(setting))
        elif len(setting.split()) == 2:
            settings_list.append(Setting.from_record(setting).convert(unit='%'))
        elif len(setting.split()) > 3:
            for element in chunkit(setting.split()):
                settings_list.append(
                    Setting.from_list(element).convert(unit='%'))
    return tuple(settings_list)


def columns_pars(head_str: str):
    """Функция для парсинга строки загаловка таблицы,
    возвращает массив с названиями всех столбцов
    данной таблицы, за исключением 'Compound'

    Arguments
    ---------
    head_str: str
        Строка - загаловок таблицы

    Return
    ------
    Возвращает кортеж со именами колонок в таблице CosmoTherm,
    за исключением 'Compound'

    Example
    -------
    >>> columns_pars('Nr Compound H ln(gamma) pv Gsolv pvExp HpvExp GpvExp')
    ('Nr', 'H', 'ln(gamma)', 'pv', 'Gsolv', 'pvExp', 'HpvExp', 'GpvExp')
    """
    return tuple(filter(lambda x: x != 'Compound', head_str.split()))

# TODO Объединить функции idexes_pars и parameters_pars


def indexes_pars(parameters: list or tuple):
    """Функция для парсинга строки загаловка таблицы,
    возвращает массив с названиями всех столбцов
    данной таблицы, за исключением 'Compound'.
    Проходит по всем строкам и берет из них только второй элемент.

    Arguments
    ---------
    parameters: list or tuple
        Список содержайщий строки с данными расчета CosmoTherm

    Return
    ------
    Возвращает список содержайщий имена веществ, заданных в
    таблице *.tab файла CosmoTherm

    Example
    -------
    >>> parameters = ['1 dbunew 7.9345E-10 0.31479727 5.7916E-07 -11.11061250',
    ...               '2 dbu+new 6.3253E-33 2.96259067 3.2692E-31 -33.6383173',
    ...               '3 cosmo1 3.0623E-36 -5.34179718 6.3968E-31 -36.8714363',
    ...               '4 cosmo2 2.3622E-44 -4.50125249 2.1291E-39 -44.7837135',
    ...               '5 cosmo3 1.0057E-48 -2.99155560 2.0031E-44 -49.0465532',
    ...               '6 cosmo4 1.9260E-40 -4.55722446 1.8359E-35 -40.9690089']
    >>> indexes_pars(parameters)
    ('dbunew', 'dbu+new', 'cosmo1', 'cosmo2', 'cosmo3', 'cosmo4')
    """
    return tuple(map(lambda x: x.split()[1], parameters))


def parameters_pars(parameters: list or tuple):
    """Проходит по всем строр
    """
    new_parameters = []
    for line in parameters:
        new_parameters.append([line.split()[0]] + line.split()[2:])
    return new_parameters


class Job:
    """
    Arguments
    ---------
    data: list or tuple
        Данные из одного "Job" в cosmo

    Atributes
    ---------
    setting:
        Набор настроек данного джоба

    units:
        Единицы измерения

    parameters:
        Данные расчетов cosmotherm

    Methods
    -------

    """
    __slots__ = ('units', 'settings', 'parameters', 'job_indx')

    def __init__(self, job: list or tuple):
        pass
        # setting = setting_pars(job[0])
        # units = job[1]
        # parameters = []
        # job_indx = 1


class Jobs:
    """
    Arguments
    ---------
    Methods
    -------
    get_csv():
    """
    pass


def main():
    import doctest
    print(doctest.testmod())


if __name__ == '__main__':
    main()
