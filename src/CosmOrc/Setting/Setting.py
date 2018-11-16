__author__ = 'Anton Domnin'
__license__ = 'GPL3'
__maintainer__ = 'Anton Domnin'
__email__ = 'a.v.daomnin@gmail.com'
__all__ = ('Setting')
# %%
import time
import pandas as pd


class Setting:
    '''
    >>> a = Setting.from_record('T 274 K')
    >>> print(a.name)
    T
    '''
    __slots__ = ('name', 'value', 'unit', 'spec_name')

    def __init__(self, name=None, value=None, unit=None, spec_name=None):
        self.spec_name = spec_name
        self.name = str(name)
        self.value = float(value)
        self.unit = unit
        if not unit:
            self.unit = ''
            print(self, 'This setting have no unit!!!')

    @classmethod
    def from_list(cls, data=None):
        # TODO дописать условие для не списков!
        if isinstance(data, (list, tuple)):

            if len(data) == 3:
                return cls(name=data[0],
                           value=data[1],
                           unit=data[2])

            elif len(data) == 2:
                return cls(name=data[0],
                           value=data[1])

            else:
                raise ValueError("Must have 3 or 2 arguments")

        else:
            pass

    @classmethod
    def from_record(cls, data=None):
        # TODO Дописать условие для не строк
        if isinstance(data, str):
            return Setting.from_list(data=data.split())

        else:
            pass

    def __repr__(self):
        return 'Setting({}, {}, {})'.format(self.name,
                                            self.value,
                                            self.unit)

    def __str__(self):
        return 'name = {}, value = {}, unit = {}'.format(self.name,
                                                         self.value,
                                                         self.unit)

    def __add__(self, other):
        # Addition
        if isinstance(other, Setting):
            if other.unit == self.unit:
                return Setting(name=self.name,
                               value=self.value + other.value,
                               unit=self.unit,
                               spec_name=self.name + ' + ' + other.name)

            # check units
            else:
                print(f'''For addition both settings
                must have same units\n {self}\t{other}''')
#
               # _koef = input('is it ok?[y/n]')
#
               # while _koef not in ('YNyn'):
               #     _koef = input('[y/n]?')
#
               #     if _koef in 'Yy':
                return Setting(name=self.name,
                               value=self.value + other.value,
                               unit=self.unit,
                               spec_name=self.name + ' + ' + other.name
                               )

                #    elif _koef in 'Nn':
                #        pass

    def __iadd__(self, other):
        # Autoaddition +=
        if isinstance(other, Setting):
            if other.unit == self.unit:
                self.value += other.value
                return self
            # check units
            else:
                print(f'''For addition both settings
                must have same units\n {self}\t{other}''')
                #_koef = input('is it ok?[y/n]')
                # while _koef not in ('YNyn'):
                #    _koef = input('[y/n]?')
                #    if _koef in 'Yy':
                self.value + other.value
                return self

                #    elif _koef in 'Nn':
                #        pass

        elif isinstance(other, (float, int)):
            return Setting(name=self.name,
                           value=self.value + other,
                           unit=self.unit)
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __sub__(self, other):
        # Subtraction
        if isinstance(other, (float, int)):
            return Setting(name=self.name,
                           value=self.value - other,
                           unit=self.unit)

        elif isinstance(other, Setting):
            if other.unit == self.unit:
                return Setting(name=self.name,
                               value=self.value - other,
                               unit=self.unit)
            # check units
            else:
                print(f'''For addition both settings must
                    have same units\n {self}\t{other}''')
                #_koef = input('is it ok?[y/n]')
                # while _koef not in ('YNyn'):
                #    _koef = input('[y/n]?')
                #    if _koef in 'Yy':
                return Setting(name=self.name,
                               value=self.value - other.value,
                               unit=self.unit,
                               spec_name=self.name + ' - ' + other.name
                               )
                #    elif _koef in 'Nn':
                #        pass
        else:
            print(f'other : {other}\nother.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __isub__(self, other):
        # -=
        if isinstance(other, Setting):

            if other.unit == self.unit:
                self.value -= other.value
                return self

            # check units
            else:
                print(f'''For addition both settings
                must have same units\n {self}\t{other}''')
                #_koef = input('is it ok?[y/n]')
#
                # while _koef not in ('YNyn'):
                #    _koef = input('[y/n]?')
#
                #    if _koef in 'Yy':
                self.value -= other.value
                return self

                # elif _koef in 'Nn':
                #     pass

        elif isinstance(other, (float, int)):
            self.value -= other
            return self
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __mul__(self, other):
        # Multiplication
        if isinstance(other, Setting):
            return Setting(name=self.name + ' * ' + other.name,
                           value=self.value * other.value,
                           unit=self.unit + ' * ' + other.unit)
        elif isinstance(other, (int, float)):
            return Setting(name=self.name,
                           value=self.value * other,
                           unit=self.unit)
        else:
            print(f'other : {other}\nother.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __imul__(self, other):
        if isinstance(other, Setting):
            self.name += ' * ' + other.name
            self.value *= other.value,
            self.unit += ' * ' + other.unit
            return self
        elif isinstance(other, (int, float)):
            self.value *= other
            return self
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __truediv__(self, other):
        # Division
        if isinstance(other, Setting):
            return Setting(name=self.name + ' / ' + other.name,
                           value=self.value / other.value,
                           unit=self.unit + ' / ' + other.unit)
        elif isinstance(other, (int, float)):
            return Setting(name=self.name,
                           value=self.value / other,
                           unit=self.unit)
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __itruediv__(self, other):
        if isinstance(other, Setting):
            self.name += ' / ' + other.name
            self.value /= other.value,
            self.unit += ' / ' + other.unit
            return self
        elif isinstance(other, (int, float)):
            self.value /= other
            return self
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __floordiv__(self, other):
        # division
        if isinstance(other, Setting):
            return Setting(name=self.name + ' // ' + other.name,
                           value=self.value // other.value,
                           unit=self.unit + ' // ' + other.unit)
        elif isinstance(other, (int, float)):
            return Setting(name=self.name,
                           value=self.value // other,
                           unit=self.unit)
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __ifloordiv__(self, other):
        # TODO create idiv
        if isinstance(other, Setting):
            self.name += ' // ' + other.name
            self.value //= other.value,
            self.unit += ' // ' + other.unit
            return self
        elif isinstance(other, (int, float)):
            self.value //= other
            return self
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __pow__(self, other):
        # Power (x**y)
        if isinstance(other, Setting):
            return Setting(name=self.name + ' ^ ' + other.name,
                           value=self.value ** other.value,
                           unit=self.unit + ' ^ ' + other.unit)
        elif isinstance(other, (int, float)):
            return Setting(name=self.name,
                           value=self.value ** other,
                           unit=self.unit)
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __ipow__(self, other):
        # autopower **=
        if isinstance(other, Setting):
            self.name += ' ^ ' + other.name
            self.value **= other.value,
            self.unit += ' ^ ' + other.unit
            return self
        elif isinstance(other, (int, float)):
            self.value **= other
            return self
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __lt__(self, other):
        # TODO create <
        '''x < y вызывает x.__lt__(y)'''
        if isinstance(other, Setting):
            if self.unit == other.unit and self.value < other.value:
                return True
        elif isinstance(other, (int, float)):
            if self.value < other:
                return True
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __le__(self, other):
        # TODO create =<
        '''x ≤ y вызывает x.__le__(y)'''
        if isinstance(other, Setting):
            if self.unit == other.unit and self.value <= other.value:
                return True
        elif isinstance(other, (int, float)):
            if self.value <= other:
                return True
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __eq__(self, other):
        # TODO create ==
        '''x == y вызывает x.__eq__(y)'''
        if isinstance(other, Setting):
            if self.unit == other.unit and self.value == other.value:
                return True
        elif isinstance(other, (int, float)):
            if self.value == other:
                return True
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __ne__(self, other):
        # TODO create !=
        '''x != y вызывает x.__ne__(y)'''
        if isinstance(other, Setting):
            if self.unit != other.unit or self.value != other.value:
                return True
        elif isinstance(other, (int, float)):
            if self.value != other:
                return True
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __gt__(self, other):
        # TODO create >
        '''x > y вызывает x.__gt__(y)'''
        if isinstance(other, Setting):
            if self.unit == other.unit and self.value > other.value:
                return True
        elif isinstance(other, (int, float)):
            if self.value > other:
                return True
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')

    def __ge__(self, other):
        # TODO create
        '''x ≥ y вызывает x.__ge__(y).'''
        if isinstance(other, Setting):
            if self.unit == other.unit and self.value >= other.value:
                return True
        elif isinstance(other, (int, float)):
            if self.value >= other:
                return True
        else:
            print(f'other : {other}\n other.type : {type(other)}')
            raise ValueError('Arguments must be Setting or number')


def main():
    a = Setting.from_list(('T', 250, 'C'))
    b = Setting.from_record('T 123 K')
    c = pd.Series(data=(a, b, a, b))
    print(c*5)


if __name__ == '__main__':
    import doctest
    start_time = time.time()
    print(doctest.testmod())
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
