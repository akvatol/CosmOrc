# %%
import sys
import unittest
sys.path.insert(0,
                '/home/antondomnin/Projects/CosmOrc/CosmOrc/src/CosmOrc/Setting')
import Setting


class TestSetting(unittest.TestCase):
    def setUp(self):
        self.T = Setting.Setting(name='T', value=122, unit='K')
        self.G = Setting.Setting(name='G', value=223, unit='kJ/mol')
        self.S = Setting.Setting(name='S', value=111, unit='J/mol/K')
        self.Tc = Setting.Setting(name='T', value=293, unit='C')

    def test_init(self):
        self.assertEqual((self.T.name, self.T.value, self.T.unit),
                         ('T', float(122), 'K'),
                         'Произошла ошибка в модуле Setting')

        self.assertEqual((self.G.name, self.G.value, self.G.unit),
                         ('G', float(223), 'kJ/mol'),
                         'Произошла ошибка в модуле Setting')

        self.assertEqual((self.S.name, self.S.value, self.S.unit),
                         ('S', float(111), 'J/mol/K'),
                         'Произошла ошибка в модуле Setting')

        self.assertEqual((self.Tc.name, self.Tc.value, self.Tc.unit),
                         ('T', float(293), 'C'),
                         'Произошла ошибка в модуле Setting')

    def test_fromlist(self):
        test_list1 = ['T', 222, 'K']
        test_list2 = ['G', -50, 'J']
        test_list3 = ['C', 15.0]
        

if __name__ == '__main__':
    print(unittest.main())
