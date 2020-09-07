import numpy as np
import pandas as pd


class Setting:
    '''
    One of the basic modules of the program
    is needed to store information, as well
    as correct mathematical operations with them.

    Atributes
    ---------
    name: str
        parameter name

    value: float
        parameter value

    unit: str
        parameter unit

    spec_name: str
        special parameter name, sometimes need for debuging

    Methods
    -------
    from_list(data: list or tuple)
        The method creates a setting class object
        from the list. The length of the list should be 3 or 2.
        In next order ('name', value, 'unit')
    return: Setting(...)

    from_record(record: str)
        The string must contain 3 or 2 words
        in next order: 'name value unit'
    return: Setting(...)

    convert(name: str, (value or koef): int or float, unit: str)
        Функция для изменения параметров объекта и конвертации
        одних единиц измерения в другие
    return: None

    Example
    -------
    >>> a = Setting.from_record('T 274 K')
    >>> b = Setting.from_list(['T', 123, 'K'])
    >>> c = Setting(name='G', value=115)
    '''
    __slots__ = ('name', 'value', 'unit', 'spec_name')

    def __init__(self, name=None, value=None, unit=None, spec_name=None):
        self.spec_name = spec_name
        self.name = str(name).strip()
        # не помню зачем это нужно
        #self.name = str(name).lower().strip()
        try:
            self.value = float(value)
        except Exception as e:
            print(e)
            raise ValueError(f"Python could not convert {value} to float")

        if unit:
            self.unit = str(unit)
        else:
            self.unit = ''

    @classmethod
    def from_list(cls, data=None):
        # TODO Написать документацию
        if isinstance(data, (list, tuple)):

            if len(data) == 3:
                return cls(name=data[0], value=data[1], unit=data[2])

            elif len(data) == 2:
                return cls(name=data[0], value=data[1])

            else:
                raise ValueError("Must have 3 or 2 arguments")

        else:
            raise TypeError("from_list() method get list or tuple")

    @classmethod
    def from_record(cls, data=None):
        # TODO Написать документацию
        if isinstance(data, str):
            return Setting.from_list(data=data.split())
        elif isinstance(data, (list, tuple)):
            return Setting.from_list(data=data)
        else:
            raise TypeError("from_record() method must get string")

    def convert(self, name=None, koef=None, value=None, unit=None):
        # TODO дописать документацию
        """
        Функция нужна для конвертации одних единиц измерения в другие,
        с её помощью можно изменить не только значения объекта Setting,
        но и изменить его имя и/или единицы измерения.

        Attributes
        ----------
        name: str
            Новое значение парметра name исходного объекта

        koef: int or float, function
            Коэффициент на который умножится исходное
            значение value исходного объекта

        value: int or float
            Новое значение параметра value исходного объекта

        unit: str
            Новое значение параметра unit исходного объекта

        Return
        ------
        None

        Examples
        --------
        >>> a = Setting(name='Energy', value=1000, unit='J')
        >>> a.convert(koef=10**(-3), unit='kJ')
        Energy 1.0 kJ

        >>> a.convert(name='NotEnergy', value=123, unit='NotJ')
        NotEnergy 123.0 NotJ
        """
        # TODO написать isinstance for value and koef
        if name:
            self.name = str(name).lower().strip()
        if koef and value:
            raise ValueError("Convert must have only koef or value")
        if koef:
            if callable(koef):
                self.value = koef(self.value)
            elif isinstance(koef, (int, float)):
                self.value *= koef
            else:
                raise TypeError
        if value:
            self.value = float(value)
        if unit:
            self.unit = str(unit)
        return self

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{} {} {}'.format(self.name, self.value, self.unit)

    def __neg__(self):
        """Определяет поведение для отрицания(-Setting)
        """
        self.value = -self.value
        return self

    def __add__(self, other):
        """
        Addition
        """
        if isinstance(other, Setting):
            if other.unit == self.unit:
                return Setting(
                    name=self.name,
                    value=self.value + other.value,
                    unit=self.unit)
            else:
                raise ValueError("For + - both settings must have same units")

        elif isinstance(other, (np.ndarray, pd.Series, pd.DataFrame)):
            return (other.__radd__(self))

        elif isinstance(other, (float, int)):
            return Setting(
                name=self.name, value=self.value + other, unit=self.unit)

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __iadd__(self, other):
        # Autoaddition +=
        if isinstance(other, Setting):

            if other.unit == self.unit:
                self.value += other.value
                return self

            else:
                raise ValueError("For + - both settings must have same units")

        elif isinstance(other, (float, int)):
            self.value += other
            return self

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __radd__(self, other):
        # Right addition (3 + T)
        if isinstance(other, Setting):
            if other.unit == self.unit:
                return Setting(
                    name=self.name,
                    value=self.value + other.value,
                    unit=self.unit)
            else:
                raise ValueError("For + - both settings must have same units")

        elif isinstance(other, (float, int)):
            return Setting(
                name=self.name, value=self.value + other, unit=self.unit)

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __sub__(self, other):
        # Subtraction
        if isinstance(other, (float, int)):
            return Setting(
                name=self.name, value=self.value - other, unit=self.unit)

        elif isinstance(other, (np.ndarray, pd.Series, pd.DataFrame)):
            return (other.__rsub__(self))

        elif isinstance(other, Setting):
            if other.unit == self.unit:
                return Setting(
                    name=self.name,
                    value=self.value - other.value,
                    unit=self.unit)
            else:
                raise ValueError("For + - both settings must have same units")
        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __isub__(self, other):
        # -=
        if isinstance(other, Setting):

            if other.unit == self.unit:
                self.value -= other.value
                return self

            else:
                raise ValueError("For + - both settings must have same units")

        elif isinstance(other, (float, int)):
            self.value -= other
            return self

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __rsub__(self, other):
        # Right - (3 - T)
        if isinstance(other, (float, int)):
            return Setting(
                name=self.name, value=other - self.value, unit=self.unit)

        elif isinstance(other, Setting):
            if other.unit == self.unit:
                return Setting(
                    name=self.name,
                    value=other.value - self.value,
                    unit=self.unit)
            else:
                raise ValueError("For + - both settings must have same units")
        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __mul__(self, other):
        # Multiplication
        if isinstance(other, Setting):
            return Setting(
                name=self.name + '*' + other.name,
                value=self.value * other.value,
                unit=self.unit + '*' + other.unit)

        elif isinstance(other, (np.ndarray, pd.Series, pd.DataFrame)):
            return (other.__rmul__(self))

        elif isinstance(other, (int, float)):
            return Setting(
                name=self.name, value=self.value * other, unit=self.unit)

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __imul__(self, other):
        # self *= other
        if isinstance(other, Setting):
            self.name = self.name + '*' + other.name
            self.value = self.value / other.value
            self.unit = self.unit + '*' + other.unit
            return self

        elif isinstance(other, (int, float)):
            self.value *= other
            return self

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __rmul__(self, other):
        # right multiplication ()
        if isinstance(other, Setting):
            return Setting(
                name=self.name + '*' + other.name,
                value=self.value * other.value,
                unit=self.unit + '*' + other.unit)

        elif isinstance(other, (int, float)):
            return Setting(
                name=self.name, value=self.value * other, unit=self.unit)

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __truediv__(self, other):
        # Division self / other
        if isinstance(other, Setting):
            return Setting(
                name=self.name + '/' + other.name,
                value=self.value / other.value,
                unit=self.unit + '/' + other.unit)

        elif isinstance(other, (int, float)):
            return Setting(
                name=self.name, value=self.value / other, unit=self.unit)

        elif isinstance(other, (np.ndarray, pd.Series, pd.DataFrame)):
            return (other.__rtruediv__(self))

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __itruediv__(self, other):
        # Autodivision /=
        if isinstance(other, Setting):
            self.name = self.name + '/' + other.name
            self.value = self.value / other.value
            self.unit = self.unit + '/' + other.unit
            return self

        elif isinstance(other, (int, float)):
            self.value /= other
            return self

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __rtruediv__(self, other):
        # Right division other / self
        if isinstance(other, Setting):
            return Setting(
                name=other.name + '/' + self.name,
                value=other.value / self.value,
                unit=other.unit + '/' + self.unit)

        elif isinstance(other, (int, float)):
            return Setting(
                name=self.name, value=other / self.value, unit=self.unit)

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __pow__(self, other):
        # Power (x**y)
        if isinstance(other, Setting):
            return Setting(
                name=self.name + '^' + other.name,
                value=self.value**other.value,
                unit=self.unit + '^' + other.unit)

        elif isinstance(other, (int, float)):
            return Setting(
                name=self.name,
                value=self.value**other,
                unit=self.unit + '*' + str(other.value))

        # elif isinstance(other, (np.ndarray, pd.Series, pd.DataFrame)):
        #     return other**self

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __rpow__(self, other):
        if isinstance(other, Setting):
            return Setting(
                name=self.name + '^' + other.name,
                value=self.value**other.value)

        elif isinstance(other, (int, float)):
            return Setting(
                name=self.name,
                value=self.value**other,
                unit=self.unit + '^' + str(other))

        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __lt__(self, other):
        '''x < y вызывает x.__lt__(y)'''
        if isinstance(other, Setting):
            if self.unit == other.unit and self.value < other.value:
                return True
            else:
                return False
        elif isinstance(other, (int, float)):
            if self.value < other:
                return True
            else:
                return False
        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __le__(self, other):
        '''x ≤ y вызывает x.__le__(y)'''
        if isinstance(other, Setting):
            if self.unit == other.unit and self.value <= other.value:
                return True
            else:
                return False
        elif isinstance(other, (int, float)):
            if self.value <= other:
                return True
            else:
                return False
        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __eq__(self, other):
        '''x == y вызывает x.__eq__(y)'''
        if isinstance(other, Setting):
            if self.unit == other.unit and self.value == other.value:
                return True
            else:
                return False
        elif isinstance(other, (int, float)):
            if self.value == other:
                return True
            else:
                return False
        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __ne__(self, other):
        '''x != y вызывает x.__ne__(y)'''
        if isinstance(other, Setting):
            if self.unit != other.unit or self.value != other.value:
                return True
            else:
                return False
        elif isinstance(other, (int, float)):
            if self.value != other:
                return True
            else:
                return False
        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __gt__(self, other):
        '''x > y вызывает x.__gt__(y)'''
        if isinstance(other, Setting):
            if self.unit == other.unit and self.value > other.value:
                return True
            else:
                return False
        elif isinstance(other, (int, float)):
            if self.value > other:
                return True
            else:
                return False
        else:
            raise TypeError("Only numbers and Settings can use in math")

    def __ge__(self, other):
        '''x ≥ y вызывает x.__ge__(y).'''
        if isinstance(other, Setting):
            if self.unit == other.unit and self.value >= other.value:
                return True
            else:
                return False
        elif isinstance(other, (int, float)):
            if self.value >= other:
                return True
            else:
                return False
        else:
            raise TypeError("Only numbers and Settings can use in math")


def main():
    pass


if __name__ == '__main__':
    import doctest
    print(doctest.testmod())
    main()
