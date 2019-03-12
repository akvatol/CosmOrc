import unittest
import random
import sys
from src.CosmOrc.basic.setting import Setting

letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


class TestSetting(unittest.TestCase):
    def setUp(self):
        self.T = Setting(name='T', value=100, unit='K')
        self.G = Setting(name='G', value=100, unit='kJ/mol')
        self.S = Setting.from_list(['T', 100, 'K'])
        self.C = Setting.from_record('S 100 J')

    def test_init(self):
        """Проверяет правильно ли инициализируются объекты
        """
        self.assertEqual((self.T.name, self.T.value, self.T.unit),
                         ('T', float(100), 'K'),
                         'Произошла ошибка в модуле Setting')

        self.assertEqual((self.G.name, self.G.value, self.G.unit),
                         ('G', float(100), 'kJ/mol'),
                         'Произошла ошибка в модуле Setting')

        self.assertEqual((self.S.name, self.S.value, self.S.unit),
                         ('T', float(100), 'K'),
                         'Произошла ошибка в модуле Setting')

        self.assertEqual((self.C.name, self.C.value, self.C.unit),
                         ('S', float(100), 'J'),
                         'Произошла ошибка в модуле Setting')

    def test_fromlist(self):
        """Проверяет правильность работы метода from_list()
        """
        # test for list with len == 3
        for i in range(10 + 1):
            name = random.choice(letters)
            value = random.randint(0, 100)
            unit = name = random.choice(letters)
            self.assertEqual(Setting.from_list([name, value, unit]),
                             Setting(name=name, value=value, unit=unit),
                             """Метод from_list(), работает некорректно
                             для списка длинной 3""")

        # test for list with len == 2
        for i in range(10 + 1):
            name = random.choice(letters)
            value = random.randint(0, 100)
            self.assertEqual(Setting.from_list([name, value]),
                             Setting(name=name, value=value),
                             """Метод from_list(), работает некорректно
                             для списка длинной 2""")

        # Errors test len == 4
        for i in range(10+1):
            name = random.choice(letters)
            value = random.randint(0, 100)
            with self.assertRaises(Exception) as context:
                Setting.from_list([name, value, name, value])

            self.assertTrue("Must have 3 or 2 arguments"
                            in str(context.exception),
                            """Метод from_list(), работает некорректно
                            для списка длинной >3""")

        for i in range(10+1):
            with self.assertRaises(Exception) as context:
                Setting.from_list(name + name)

            self.assertTrue("from_list() method get list or tuple"
                            in str(context.exception),
                            """Метод from_list(), работает некорректно
                            для не списка""")

    def test_fromrecord(self):
        """Проверяет правильность работы метода from_record()
        """
        # test for list with len == 3
        for i in range(10 + 1):
            name = random.choice(letters)
            value = random.randint(0, 100)
            unit = name = random.choice(letters)
            self.assertEqual(Setting.from_record(f'{name} {value} {unit}'),
                             Setting(name=name, value=value, unit=unit),
                             """Метод from_record(), работает некорректно
                             для строки с 3 словами""")

        # test for list with len == 2
        for i in range(10 + 1):
            name = random.choice(letters)
            value = random.randint(0, 100)
            self.assertEqual(Setting.from_record(f'{name} {value}'),
                             Setting(name=name, value=value),
                             """Метод from_record(), работает некорректно
                             для строки с 2 словами""")

        # Errors test len == 4
        for i in range(10+1):
            name = random.choice(letters)
            value = random.randint(0, 100)
            with self.assertRaises(Exception) as context:
                Setting.from_record(f'{name, value, name, value}')

            self.assertTrue("Must have 3 or 2 arguments"
                            in str(context.exception),
                            """Метод from_record(), работает некорректно
                             для строки с > 3 словами""")
        # test bad string
        for i in range(10+1):
            name = random.choice(letters)
            with self.assertRaises(Exception) as context:
                Setting.from_record([name, name])
            self.assertTrue("Python could not" in str(context.exception))

        with self.assertRaises(Exception) as context:
            Setting.from_record(123)

        self.assertTrue("from_record() method must get string"
                        in str(context.exception))

    def test_convert(self):
        """Проверяет правильность работы метода convert
        """
        self.C.convert(name='TT')
        self.assertAlmostEqual(self.C,
                               Setting(name='TT', value=100, unit='J'),
                               """convert() работает не правильно
                               с атрибутом name""")

        self.C.convert(name=123)
        self.assertAlmostEqual(self.C,
                               Setting(name='123', value=100, unit='J'),
                               """convert() работает не правильно
                               с атрибутом name""")

        self.C.convert(name=(1, 3, 4))
        self.assertAlmostEqual(self.C,
                               Setting(name=f'{(1, 3, 4)}', value=100, unit='J'),
                               """convert() работает не правильно
                               с атрибутом name""")

    def test_neg(self):
        """Проверяет работу __neg__ (Определяет поведение для отрицания(-Setting))
        """
        self.assertEqual(-self.T, -100,
                         "__neg__ работает некорректно")
        self.assertEqual(-self.C,
                         Setting(name='S', value=-100, unit='J'),
                         "__neg__ работает некорректно")

    def test_eq(self):
        """Проверяет правильно ли работает __eq__ (x == y вызывает x.__eq__(y))
        """
        self.assertNotEqual(
            self.T, self.G, "Сравнение Setting Setting работает некорректно")
        self.assertEqual(self.T, 100, "Сравнение Setting число некорректно")
        self.assertEqual(
            self.T, self.S, "Сравнение Setting Setting некорректно")

    def test__add(self):
        """Проверяет правильно ли работает __add__ (x + y вызывает x.__add__(y))
        """

        self.assertTrue(self.T + self.S == Setting(name='T', value=200, unit='K'),
                        "__add__ Setting Setting работает некорретктно")

        self.assertTrue(self.T + 1 == 101,
                        "__add__ Setting число работает некорректно")

        with self.assertRaises(Exception) as context:
            self.T + self.G

        self.assertTrue("For + - both settings must have same units"
                        in str(context.exception))

        with self.assertRaises(Exception) as context:
            self.T + '23'

        self.assertTrue("Only numbers and Settings can use in math"
                        in str(context.exception))

    def test_iadd(self):
        """Проверяет правильно ли работает __iadd__ (x += y вызывает x.__iadd__(y))
        """
        j = self.T.value
        for i in range(0, 10 + 1):
            self.T += i
            j += i
            self.assertTrue(self.T == j,
                            "__iadd__ некоректно складывает числа и Setting")

        j = 100
        for i in range(0, 10 + 1):
            some_sett = Setting.from_list(['T', i, 'K'])
            self.S += some_sett
            j += some_sett.value
            self.assertTrue(self.S == j,
                            "__iadd__ некоректно складывает Setting и Setting")

        with self.assertRaises(Exception) as context:
            self.T += '23'

        self.assertTrue("Only numbers and Settings can use in math"
                        in str(context.exception))

    def test_radd(self):
        """Проверяет правильно ли работает __radd__ (y + x вызывает x.__radd__(y))
        """
        self.assertEqual(self.T + 1,
                         1 + self.T,
                         "__radd__ число Setting работает некорректно")

        self.assertEqual(self.C + 5,
                         5 + self.C,
                         "__radd__ число Setting работает некорректно")

        self.assertEqual(self.S + self.T,
                         self.T + self.S,
                         "__radd__ Setting Setting работает некорректно")

        with self.assertRaises(Exception) as context1:
            self.T + self.G

        self.assertTrue("For + - both settings must have same units"
                        in str(context1.exception))

        with self.assertRaises(Exception) as context2:
            self.G + self.T

        self.assertTrue("For + - both settings must have same units"
                        in str(context2.exception))

        self.assertEqual(str(context1.exception),
                         str(context2.exception),
                         """
Аномальное поведение при сравнении __radd__ и __add__
для случая Setting Setting
                         """)

    def test_sub(self):
        """Проверяет правильно ли работает __sub__ (x - y вызывает x.__sub__(y))
        """
        self.assertTrue(self.T - self.S == Setting(name='T', value=0, unit='K'),
                        "__sub__ некоректно работает для Setting - Setting")
        self.assertTrue(self.T - 1 == 99,
                        "__sub__ некоректно работает для Setting - число")

        with self.assertRaises(Exception) as context:
            self.T - self.G

        self.assertTrue("For + - both settings must have same units"
                        in str(context.exception))

        with self.assertRaises(Exception) as context:
            self.T - '23'

        self.assertTrue("Only numbers and Settings can use in math"
                        in str(context.exception))

    def test_isub(self):
        """Проверяет правильно ли работает __isub__ (x -= y вызывает x.__isub__(y))
        """
        j = self.T.value
        for i in range(0, 10 + 1):
            self.T -= i
            j -= i
            self.assertTrue(self.T == j,
                            "__isub__ некоректно вычитает числа из Setting")

        j = 100
        for i in range(0, 10 + 1):
            some_sett = Setting.from_list(['T', i, 'K'])
            self.S -= some_sett
            j -= some_sett.value
            self.assertTrue(self.S == j,
                            "__isub__ некоректно вычитает Setting из Setting")

        with self.assertRaises(Exception) as context:
            self.T -= '23'

        self.assertTrue("Only numbers and Settings can use in math"
                        in str(context.exception))

    def test_mul(self):
        """Проверяет правильно ли работает __mul__ (x * y вызывает x.__mul__(y))
        """
        self.assertTrue(self.T*self.S ==
                        Setting(name='T*T', value=100*100, unit='K*K'),
                        "__mul__ некоректно работает Setting и Setting")

        self.assertTrue(self.T*100 == 100*100,
                        "__mul__ некоректно работает Setting и число")

        self.assertTrue(self.T*self.G ==
                        Setting(name='T*T', value=100*100, unit='K*kJ/mol'),
                        "__mul__ некоректно работает Setting и Setting")

        with self.assertRaises(Exception) as context:
            self.T * '23'
        self.assertTrue("Only numbers and Settings can use in math"
                        in str(context.exception))

    def test_imul(self):
        """Проверяет правильно ли работает __imul__ (x *= y вызывает x.__imul__(y))
        """

        self.assertEqual(self.T.__imul__(self.T),
                         self.T.value * self.T.value,
                         "__imul__ некоректно работает с Setting Setting")

        self.assertEqual(self.T.value * 2,
                         self.T.__imul__(2),
                         "__imul__ работает некоректно для Setting * число")

        with self.assertRaises(Exception) as context:
            self.T *= '23'

        self.assertTrue("Only numbers and Settings can use in math"
                        in str(context.exception))

    def test_div(self):
        """Проверяет правильно ли работает __truediv__ и __itruediv__
        (x / y вызывает x.__div__(y), x /= y вызывает x.__idiv__(y))
        """

        self.assertTrue(self.G/self.T == Setting.from_record("G/T 1 kJ/mol/K"),
                        "__truediv__ работает некоректно для Setting и Setting")
        self.assertTrue(self.T/2 == 50,
                        "__truediv__ работает некоректно для Setting и число")
        self.assertTrue(self.T.__itruediv__(2) == 50,
                        "__itruediv__ работает некоректно для Setting и число")
        self.assertEqual(self.G.__itruediv__(self.S),
                         Setting.from_record("G/T 1 kJ/mol/K"),
                         "__itruediv__ работает некоректно для Setting и Setting")

        with self.assertRaises(Exception) as context:
            self.T.__itruediv__('23')

        self.assertTrue("Only numbers and Settings can use in math"
                        in str(context.exception))

        with self.assertRaises(Exception) as context:
            self.T.__truediv__('23')

        self.assertTrue("Only numbers and Settings can use in math"
                        in str(context.exception))

    def test_pow(self):
        """Проверяет правильность работы __pow__ и __rpow__
        (x**y вызывает x.__pow__(y))
        """


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSetting)
    unittest.TextTestRunner(verbosity=2).run(suite)
