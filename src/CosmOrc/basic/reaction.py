import glob
import logging
import os
import random

import numpy as np
import pandas as pd

from typing import List, Set, Dict, Tuple, Any
from typing import Callable, Iterable, Union, Optional, List

from src.CosmOrc.basic.compound import Compound, gibbs_energy, enthalpy
from src.CosmOrc.parsers.cospar import Jobs
from src.CosmOrc.basic._basic import timeit

DEFAULT_CONDITION: Dict[str, List[Union[int, float]]] = {
    "temperature": [298.15],
    "pressure": [1],
}

R = 8.31441

# TODO Пренести логер в майн, ну и поправить логирование
# code from https://docs.python.org/3/howto/logging-cookbook.html
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler("app.log", mode="w")
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    "%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s"
)
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)


# TODO: Нужно считать иначе, написать отдельные функции для расчета
# параметров из космы и т.д., а потом из них составить функцию для реакции.

class Reaction:
    def __init__(self, name: str, reaction: List[Dict[Compound, int]]):

        self.name = name
        # reaction looks like ({Compound1: 2, Compound2: 3}, {Compound3: 1, Compound4: 2})
        # 2*Compound1 + 3*Compound2 = Compound3 + 2*Compound4
        self.reaction = reaction

        logger.info(
            f"Reaction(name={self.name}, reaction={self.reaction}) successfully initialized"
        )

    def __repr__(self):
        _repr_ = f"Reaction(name={self.name}, reaction={self.reaction})"
        return _repr_

    def addition(self, other: Union[Compound, Dict[Compound, int]]):

        if isinstance(other, Compound):
            self.reaction[0].update({other: 1})
        elif isinstance(other, dict):
            self.reaction[0].update(other)
        # elif isinstance(other, Reaction):
        #     self.reaction[0].update(other.reaction[0])
        #     self.reaction[1].update(other.reaction[1])
        else:
            # TODO Написать текст для ошибки
            logger.error(f"Try add {other} to {self}")
            raise ValueError("Some text")
        return self

    def substraction(self, other: Union[Compound, Dict[Compound, int]]):

        if isinstance(other, Compound):
            self.reaction[1].update({other: 1})
        elif isinstance(other, dict):
            self.reaction[1].update(other)
        # elif isinstance(other, Reaction):
        #     self.reaction[0].update(other.reaction[1])
        #     self.reaction[1].update(other.reaction[0])
        else:
            # TODO Написать текст для ошибки
            logger.error(f"Try add {other} to {self}")
            raise ValueError("Some text")
        return self

    def _gibbs_energy(
        self, conditions: Dict[str, List[Union[float, int]]] = DEFAULT_CONDITION
    ) -> pd.DataFrame:

        # TODO: Объединить повторяющиеся фрагменты кода в функцию
        GE0 = 0
        GE1 = 0
        Ggas: pd.DataFrame

        logger.info(f"Start gibbs_energy calc for {self.name}")
        logger.debug(f"{conditions}")

        # Calculate sum of Gibbs Energy for reagents
        for reagents in self.reaction[0].keys():
            logger.debug(
                f"{self.reaction[0][reagents]}*{reagents.name} Gibbs Energy calc"
            )
            reaction_coefficient = self.reaction[0][reagents]
            GE0 += reaction_coefficient * gibbs_energy(
                compound=reagents,
                temperature=conditions["temperature"],
                pressure=conditions["pressure"],
            )

        # Calculate sum of Gibbs Energy for products
        for products in self.reaction[1].keys():
            logger.debug(
                f"{self.reaction[1][products]}*{products.name} Gibbs Energy calc"
            )

            reaction_coefficient = self.reaction[1][products]
            GE1 += reaction_coefficient * gibbs_energy(
                compound=products,
                temperature=conditions["temperature"],
                pressure=conditions["pressure"],
            )

        Ggas = GE1 - GE0

        return Ggas.T

    def _gibbs_energy_reagents_cosmo(
        self,
        cosmo_settings: pd.DataFrame,
        compound: Compound,
    ):

        index = cosmo_settings.index
        data = []

        # GE = 0
        logger.info('Gibbs energy for compound start calc')
        logger.debug(f'Compound:{compound.name}')
        for job in index:
            # TODO: костыль , нужен т.к. иначе не работает с ошибкой TypeError: 'numpy.float64' object is not iterable
            # или TypeError: can't multiply sequence by non-int of type 'float'
            temperature = np.array([cosmo_settings["T="].loc[job]])
            pressure = np.array([cosmo_settings["p="].loc[job]])
            GE = gibbs_energy(compound=compound,
                              temperature=temperature, pressure=pressure)
            data.append(GE.iat[0, 0])
            logger.debug(f'T=:{temperature}, p={pressure}, value={GE}')
        df = pd.Series(index=index, data=data)
        return df

    def gibbs_energy_cosmo(
            self,
            cosmo_file: str):

        # Reading data from *.tab file
        cosmo_data = Jobs(path=cosmo_file)
        cosmo_solv_data = cosmo_data.small_df(
            ["Gsolv", "ln(gamma)", "Nr"], invert=True)
        cosmo_setting = cosmo_data.settings_df()

        logger.info(f"Gibbs energy calc start tab file {cosmo_file}")

        # TODO: Собрать Ggas по джобам, чтобы Gsolv и Ggas имели одинаковую структуру
        G0 = 0
        G1 = 0
        for reagents in self.reaction[0].keys():

            reaction_coefficient = self.reaction[0][reagents]
            reagents_nr = cosmo_solv_data["Nr"].loc[reagents.name].values[0]
            # Умножаем на коэффициент, так как cospar
            # !!!! не переводит значение энергии в джоули !!!!!
            G0 += reaction_coefficient * \
                cosmo_solv_data["Gsolv"].loc[reagents.name] * 4184
            if reagents.ideal:
                pass
            else:
                activity = (
                    np.log(cosmo_setting.loc[str(reagents_nr)].T)
                    + cosmo_solv_data["ln(gamma)"].loc[reagents.name]
                )
                G0 += reaction_coefficient * activity * \
                    R * cosmo_setting.loc["T="].T

            # Gas phase part
            G0 += reaction_coefficient * self._gibbs_energy_reagents_cosmo(
                compound=reagents, cosmo_settings=cosmo_setting.T
            )

        for products in self.reaction[1].keys():

            reaction_coefficient = self.reaction[1][products]
            products_nr = str(
                cosmo_solv_data["Nr"].loc[products.name].values[0])
            # Умножаем на коэффициент, так как cospar
            # !!!! не переводит значение энергии в джоули !!!!!
            G1 += reaction_coefficient * \
                cosmo_solv_data["Gsolv"].loc[products.name] * 4184
            if products.ideal:
                pass
            else:
                ln_x = np.log(cosmo_setting.loc[str(products_nr)].T)
                ln_gamma = cosmo_solv_data["ln(gamma)"].loc[products.name]
                activity = ln_x + ln_gamma

                G1 += reaction_coefficient * activity * \
                    R * cosmo_setting.loc["T="].T
            G1 += reaction_coefficient * self._gibbs_energy_reagents_cosmo(
                compound=products, cosmo_settings=cosmo_setting.T
            )

        return G1 - G0

    def gibbs_energy_reaction(
            self,
            conditions: Dict[str, List[Union[float, int]]] = DEFAULT_CONDITION,
            cosmo_file: str = None) -> pd.DataFrame:

        if cosmo_file:
            Gtot = self.gibbs_energy_cosmo(cosmo_file)
        else:
            Gtot = self._gibbs_energy(conditions=conditions)

        return Gtot

    def energy_gas_compound(
            self,
            compound: Compound,
            conditions: Dict[str, List[Union[float, int]]] = DEFAULT_CONDITION,
            reaction_coefficient: int = 1,
            function: Callable = gibbs_energy) -> pd.DataFrame:
        """
        Для каждой пары заданных температур и давлений cчитает энергию
        (Энергию Гиббса или энтальпию) вещества в газе, может учитывать коэффициент реакции.

        Parameters
        ----------
        compound : Compound
            Вещество для которого рассчитываются термодинамические параметры

        conditions : Dict[str, List[Union[float, int]]], optional
            Условия (Температура и давление) для которых параметр
            будет посчитан имеет вид: {'temperature':[200, 250], pressure:[1, 2]}, by default DEFAULT_CONDITION

        reaction_coefficient : int, optional
            Коэффициент на который умножиться финальное значение, by default 1

        function : Callable, optional
            Определяет какой параметр будет рассчитан (gibbs_energy, enthalpy), by default gibbs_energy

        Return
        ------
        pandas.DataFrame
            Таблицы со значениями заданного параметра
        """

        t = conditions.get('temperature')
        p = conditions.get('pressure')

        E = reaction_coefficient * function(
            compound=compound,
            temperature=t,
            pressure=p,
        )
        return E

    def energy_solv_compound(self): pass


def main():
    Comp1 = Compound(
        path_to_file="/home/antond/Загрузки/archive/iPrOH-acetone-HBr.log",
        linear=False,
        name="dbunew",
    )

    Comp2 = Compound(
        path_to_file="/home/antond/Загрузки/archive/Mn-OiPr_NH-NHC_HB.log",
        linear=False,
        name="dimethylformamide",
    )

    reac = Reaction(reaction=({Comp1: 1}, {Comp2: 2}), name="test")
    return reac.gibbs_energy_cosmo(cosmo_file="/home/antond/Загрузки/75C.tab")


if __name__ == "__main__":
    main()
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