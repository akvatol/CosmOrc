import unittest
import os
import random
import sys
import difflib
import src.CosmOrc.parsers.gauspar as gauspar
from src.CosmOrc.basic.setting import Setting

path_to_test_files = 'test/data/test_gauspar'
raw_files = path_to_test_files + '/raw_files'
out_files = path_to_test_files + '/out_files'


class TestGauspar(unittest.TestCase):
    def setUp(self):
        pass

    def test_read_data_gaussian(self):
        """gauspar.read_data_gaussian test function
        """
        out_files_list = os.listdir(out_files)
        for files in out_files_list:
            with open(raw_files + '/' + files, 'r') as f1:
                data1 = f1.readlines()
                data2 = gauspar.read_data_gaussian(out_files + '/' + files)
                self.assertFalse(
                    list(difflib.context_diff(data1, data2)),
                    'read_gausian_data method work uncorrect')

    def test_tp_pars(self):
        """gauspar.tp_pars test function
        """
        _temperature = r'(Temperature)\s*([0-9.]+)\s*([\w]+).'
        _pressure = r'(Pressure)\s*([0-9.]+)\s*([\w]+).'

        # yapf do it with my code :(

        tp_string_list = [
            'Temperature   298.150 Kelvin.  Pressure   1.00000 Atm.',
            'Temperature   223 Kelvin.  Pressure   14.00000 bar.',
            'Temperature   228 C.  Pressure   14.00000 bar.'
        ]

        tp_data_list = [[
            Setting.from_record('Temperature 298.150 Kelvin'),
            Setting.from_record('Pressure 1.00000 Atm')
        ],
                        [
                            Setting.from_record('Temperature 223 Kelvin'),
                            Setting.from_record('Pressure 14.00000 bar')
                        ],
                        [
                            Setting.from_record('Temperature 228 C'),
                            Setting.from_record('Pressure 14.00000 bar')
                        ]]

        for i in range(len(tp_string_list)):
            self.assertRegex(tp_string_list[i],
                             _temperature + r'\s*' + _pressure)
            tp = gauspar.tp_pars(tp_string_list[i])
            self.assertEqual(tp, tp_data_list[i],
                             'tp_parser function does not work')

        bad_tp_string = [
            'T   298.150 Kelvin.  Pressure   1.00000 Atm.',
            'T   298 Kelvin.  P   1 Atm.',
            'Temp   298.150 Kelvin.  Press   1.00000 Atm.'
        ]

        for bad_string in bad_tp_string:
            self.assertNotRegex(bad_string, _temperature + r'\s*' + _pressure)

    def test_freq_pars(self):
        """gauspar.freq_pars function test
        """

        _name_ = r'(\w+)'
        _freq_value_ = r'([-\d.]+)'

        reg = _name_ + r'\s\-\-\s*' + _freq_value_ + \
            r'\s*' + _freq_value_ + r'\s*' + _freq_value_

        list_with_freqs = [
            'Frequencies -- 77.1886 78.3453 95.1516',
            'Frequencies -- 52.1233 112.1232 118.1517',
            'Frequencies -- 2.0231 8.6488 10.1112'
        ]

        # make it with code generator, cool stuff
        # replace() very useful thing

        list_with_freqs_settings = [
            [
                Setting(name='freq.', value=77.1886, unit='cm**-1'),
                Setting(name='freq.', value=78.3453, unit='cm**-1'),
                Setting(name='freq.', value=95.1516, unit='cm**-1')
            ],
            [
                Setting(name='freq.', value=52.1233, unit='cm**-1'),
                Setting(name='freq.', value=112.1232, unit='cm**-1'),
                Setting(name='freq.', value=118.1517, unit='cm**-1')
            ],
            [
                Setting(name='freq.', value=2.0231, unit='cm**-1'),
                Setting(name='freq.', value=8.6488, unit='cm**-1'),
                Setting(name='freq.', value=10.1112, unit='cm**-1')
            ]
        ]

        for i in range(len(list_with_freqs)):
            self.assertRegex(
                list_with_freqs[i], reg,
                'Regular expression does not work correctly in tp_pars.')

            self.assertEqual(
                gauspar.freq_pars(list_with_freqs[i]),
                list_with_freqs_settings[i],
                'function tp_pars does not work correctly.')

    def test_parameters_pars(self):
        """gauspar.parameters_pars function test
        """

        parameters_list = [
            'Zero-point correction= 0.003467',
            'Thermal correction to Energy= 0.011897',
            'Thermal correction to Enthalpy= 0.012841',
            'Thermal correction to Gibbs Free Energy= -0.033924',
            'Sum of electronic and zero-point Energies= -3349.814800',
            'Sum of electronic and thermal Energies= -3349.806370',
            'Sum of electronic and thermal Enthalpies= -3349.805426',
            'Sum of electronic and thermal Free Energies= -3349.852191'
        ]

        # yapf do it, not me, it does not look good for me,
        # but i do not have time to fix it

        parameters_list_setting = [
            Setting(
                name='Zero-point correction',
                value=9102.392980879,
                unit='J/mol'),
            Setting(
                name='Thermal correction to Energy',
                value=31234.833946788996,
                unit='J/mol'),
            Setting(
                name='Thermal correction to Enthalpy',
                value=33713.247264917,
                unit='J/mol'),
            Setting(
                name='Thermal correction to Gibbs Free Energy',
                value=-89065.353182388,
                unit='J/mol'),
            Setting(
                name='Sum of electronic and zero-point Energies',
                value=-8794730522.862587,
                unit='J/mol'),
            Setting(
                name='Sum of electronic and thermal Energies',
                value=-8794708390.421621,
                unit='J/mol'),
            Setting(
                name='Sum of electronic and thermal Enthalpies',
                value=-8794705912.008303,
                unit='J/mol'),
            Setting(
                name='Sum of electronic and thermal Free Energies',
                value=-8794828690.60875,
                unit='J/mol')
        ]

        for i, j in list(zip(parameters_list, parameters_list_setting)):
            self.assertEqual(gauspar.parameter_pars(i), j, '')

        # Wow, seems that work good

    def test_properties_pars(self):
        """gauspar.properties_pars test function
        """
        _value_ = r'([0-9]{1,10}\.[0-9]{3})'
        _whitespace_ = r'\s{2,15}'
        reg = _value_ + _whitespace_ + _value_ + _whitespace_ + _value_

        # yapf do it
        properties_list = [
            'Total                    7.465             22.705             98.425',
            'Electronic               0.000              0.000              2.183',
            'Translational            0.889              2.981             41.751',
            'Rotational               0.889              2.981             30.134',
            'Vibrational              5.688             16.744             24.356'
        ]

        for line in properties_list:
            self.assertRegex(line, reg, 'regexp does not work')

    def test_file_pars(self):
        # TODO Доделать 
        out_files_list = os.listdir(out_files)
        for files in out_files_list:
            pass
