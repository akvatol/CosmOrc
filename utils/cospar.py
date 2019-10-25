import re

import pandas as pd
import pysnooper

from utils.setting import Setting


def chunkit(data: list or tuple = None, n: int = None):
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
    >>> chunkit(l)
    [[1, 2, 3, 4], [5, 6, 7, 8]]
    >>> chunkit(l, n=4)
    [[1, 2], [3, 4], [5, 6], [7, 8]]
    """
    new_data = []
    if not n:
        n = 2
    avg = len(data) / n
    last = 0
    while last < len(data):
        new_data.append(data[int(last) : int(last + avg)])
        last += avg
    return new_data


def read_data_cosmo(file_path: str = None) -> list:
    """Функция для чтения *.tab файлов CosmoTherm, выбирает строки с
    параметрами расчета, единицами измерения и непосредственно результатами
    расчета.

    Arguments
    ---------
    file_path: str
        Путь к *.tab файлу

    Return
    ------
    data: list
        Двумерный список, len(data) == количеству работ (job) в исходном файле,
        в каждый подмассив массива, входят данные о каждой конкретной работы
    """

    with open(file_path, "r") as file:
        data = []
        for line in file:
            if line.split():
                # Выбираем строки с параметрами расчета
                if "Setting" in line:
                    jobs_data = []
                    jobs_data.append(line)
                    data.append(jobs_data)
                # Выбираем строки с единицами измерения и данными расчетов
                elif "job" not in line or "Units" in line:
                    jobs_data.append(line)
    return data


def compound_nr(some_str: str):

    _compound_nr = r"x\(([\d]*)\)="
    _compound_nr_string = re.search(_compound_nr, some_str)
    if _compound_nr_string:
        return _compound_nr_string.group(1)

def setting_pars(settings_str: str):
    # TODO Документация job_indx
    """Функция для извлечения параметров расчета из строк,
    принимает строку из *.tab файла, содержащую подстроку
    'Settings'

    Arguments
    ---------
    settings_str: str
        Строка *.tab файла, содержащая ключевое слово 'Settings'

    Return
    ------
    job_indx: str

    settings_list: tuple
        Кортеж содержащий объекты класса Setting, описывающие
        условия проведения расчета

    Example
    -------
    >>> setting_pars('Settings  job 2 : T= 223.15 K ; x(1)= 0.1000;')
    (2, (T= 223.15 K, x(1)= 0.1 %))
    """
    settings_list = []
    job_indx, new_line = settings_str.split(":")
    job_indx = job_indx.split()[2]
    settings = new_line.split(";")
    for setting in settings:
        new_setting = None
        if len(setting.split()) == 3:
            settings_list.append(Setting.from_record(setting))
        elif len(setting.split()) == 2:
            new_setting = Setting.from_record(setting)
            new_setting.convert(name=compound_nr(new_setting.name), unit="%")
            settings_list.append(new_setting)
        elif len(setting.split()) > 3:
            # TODO: Проблемное место, пофиксить n в chunkit
            for element in chunkit(setting.split(), n=len(setting.split())/2):
                new_setting = Setting.from_record(element)
                new_setting.convert(name=compound_nr(new_setting.name), unit="%")
                settings_list.append(new_setting)
    return int(job_indx), tuple(settings_list)


def columns_pars(head_str: str):
    """Функция для парсинга строки заголовка таблицы,
    возвращает массив с названиями всех столбцов
    данной таблицы, за исключением 'Compound'

    Arguments
    ---------
    head_str: str
        Строка - заголовок таблицы

    Return
    ------
    Возвращает кортеж со именами колонок в таблице CosmoTherm,
    за исключением 'Compound'

    Example
    -------
    >>> columns_pars('Nr Compound H ln(gamma) pv Gsolv pvExp HpvExp GpvExp')
    ('Nr', 'H', 'ln(gamma)', 'pv', 'Gsolv', 'pvExp', 'HpvExp', 'GpvExp')
    """
    return tuple(filter(lambda x: x != "Compound", head_str.split()))


def data_pars(data: list or tuple):
    # TODO Documentations
    """Функция для пасинга данных одной таблицы

    Arguments
    ---------
    data: list or tuple
        Список содержащий строки с данными расчета CosmoTherm

    Return
    ------
    Возвращает список содержащий имена веществ, заданных в
    таблице *.tab файла CosmoTherm

    Example
    -------
    >>> data = ['1 dbunew 7.9345E-10 0.31479727 5.7916E-07 -11.11061250',
    ...         '2 dbu+new 6.3253E-33 2.96259067 3.2692E-31 -33.6383173',
    ...         '3 cosmo1 3.0623E-36 -5.34179718 6.3968E-31 -36.8714363',
    ...         '4 cosmo2 2.3622E-44 -4.50125249 2.1291E-39 -44.7837135',
    ...         '5 cosmo3 1.0057E-48 -2.99155560 2.0031E-44 -49.0465532',
    ...         '6 cosmo4 1.9260E-40 -4.55722446 1.8359E-35 -40.9690089']

    >>> data_pars(data)
    (['dbunew', 'dbu+new', 'cosmo1', 'cosmo2', 'cosmo3', 'cosmo4'], [['1', '7.9345E-10', '0.31479727', '5.7916E-07', '-11.11061250'], ['2', '6.3253E-33', '2.96259067', '3.2692E-31', '-33.6383173'], ['3', '3.0623E-36', '-5.34179718', '6.3968E-31', '-36.8714363'], ['4', '2.3622E-44', '-4.50125249', '2.1291E-39', '-44.7837135'], ['5', '1.0057E-48', '-2.99155560', '2.0031E-44', '-49.0465532'], ['6', '1.9260E-40', '-4.55722446', '1.8359E-35', '-40.9690089']])
    """
    compounds = []
    new_parameters = []
    for line in data:
        _ = line.split()
        compounds.append(_[1])
        new_parameters.append([_[0]] + _[2:])
    return compounds, new_parameters


class Job:
    """
    Arguments
    ---------
    data: list or tuple
        Данные из одного "job" CosmoTherm

    Attributes
    ---------
    setting:
        Набор настроек данного расчета

    units:
        Строка с информацией о некоторых единицах измерения

    parameters:
        Данные расчетов СosmoTherm

    Properties
    ----------
    full_df:

    small_df:

    settings_df:

    """

    __slots__ = ("units", "settings", "compounds", "parameters", "columns", "job_indx")

    def __init__(self, job: list or tuple):
        self.units = job[1]
        self.job_indx, self.settings = setting_pars(job[0])
        self.compounds, self.parameters = data_pars(job[3:])
        self.columns = columns_pars(job[2])
        self.settings = list(self.settings)

    def full_df(self):
        """
        Метод для получения полной информации об одной работе,
        вспомогательный метод для упрощения работы с классом
        Jobs. Сработает только если класс правильно инициализирован.

        Return
        ------
            pd.Dataframe(): Возвращает датафрейм с данными одной работы,
                index -- мультииндекс состоящий из номера работы и списка
                рассчитываемых веществ.
                columns -- названия параметров,
                data -- значения таблицы COSMOtherm
        """
        index = list(zip([self.job_indx] * len(self.compounds), self.compounds))
        multiindex = pd.MultiIndex.from_tuples(index, names=["Job", "Compound"])
        return pd.DataFrame(
            data=self.parameters, index=multiindex, columns=self.columns
        )

    def small_df(self, columns: list or tuple):
        """
        Вспомогательный метод, помогает получать одну таблицу с определенными
        столбцами. Нужен для упрощения работы с классом Jobs.

        Arguments
        ---------
            columns: list or tuple
                Список колонок
        """
        _small_df = self.full_df().loc[:, columns].copy()
        return _small_df

    def settings_df(self, detailed=None):
        # TODO Документация
        """
        """
        columns = [self.job_indx]
        index = [x.name for x in self.settings]

        if 'p=' in index:
            pass
        else:
            index.append('p=')
            self.settings.append(Setting(name='p=', value=1, unit='atm'))

        if detailed:
            data = self.settings
        else:
            data = [x.value for x in self.settings]

        return pd.DataFrame(columns=columns, index=index, data=data)


class Jobs:
    """
    Класс, хранит в себе данные одного расчета COSMOTherm.
    При инициализации принимает аргумент path: str - путь к *.tab файлу,
    автоматически считывает данные из файла и инициализирует классы Job,
    для каждой отдельной работы.

    Arguments
    ---------
        path: str
            Путь к *.tab файлу

    Methods
    -------
    full_df(csv: bool, invert: bool): df
    small_df(csv: bool, invert: bool): df
    settings_df(csv: bool): df

    for need spec df for calc
    """

    __slots__ = ("path", "data")

    def __init__(self, path: str):
        self.path = path
        self.data = [Job(i) for i in read_data_cosmo(path)]

    def full_df(self, invert=None):
        # TODO Документация
        """
        """
        df = pd.concat([job.full_df() for job in self.data], sort=True)
        df = df.applymap(lambda x: 0 if x == 'NA' else x)
        df = df.apply(pd.to_numeric)
        df.fillna(0, inplace=True)
        if invert:
            df.sort_index(axis=0, level=1, inplace=True)
            return df.swaplevel(i=-2, j=-1, axis=0)
        else:
            return df

    def small_df(self, columns: list or tuple = None, invert: bool = None):
        # TODO Документация
        """
        """
        if columns:
            _small_df = self.full_df().loc[:, columns].copy()
            if invert:
                _small_df.sort_index(axis=0, level=1, inplace=True)
                return _small_df.swaplevel(i=-2, j=-1, axis=0)
            else:
                return _small_df
        else:
            pass

    def settings_df(self, detailed=None):
        # TODO
        """[summary]

        Returns
        -------
        [type]
            [description]
        """
        if detailed:
            df = pd.concat(
                [job.settings_df(detailed=1) for job in self.data], axis=1, sort=True
            )
            df.fillna(0, inplace=True)
            return df
        else:
            df = pd.concat([job.settings_df() for job in self.data], axis=1, sort=True)
            df.fillna(0, inplace=True)
            return df






def main():
    from os import listdir
    from os.path import isfile, join
    mypath = '/home/anton/Documents/Scamt_projects/Adonin_project/COSMOthermProject/EA_scrf/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    files = [i for i in onlyfiles if i.endswith('tab')]
    for file in files:
        Jobs(mypath + file).small_df(invert=1, columns=('Gsolv', 'ln(gamma)', 'Nr')).T.to_csv(f'{mypath + file}.csv')
        Jobs(mypath + file).settings_df().T.to_csv(f'{mypath + file}_Settings.csv')


if __name__ == "__main__":
    main()
