from decimal import Decimal
import re
import os.path
import os


class Cosmo_Generator:
    # принимает шаблон и набор реакцию -> входной файл космы
    def __init__(self, template: str):
        """
        template: str
        n: str
        """
        self.template = template

    def read_template(self):
        with open(self.template, 'r') as tmp:
            head, compounds, concentrations = [], [], []
            for i in tmp:
                if i.startswith('f ='):
                    z = 1
                else:
                    z = 0
                if z:
                    compounds.append(i)
                elif not z and ('#' in i):
                    concentrations.append(i)
                    break
                else:
                    head.append(i)
        return (head, compounds, concentrations)


    def template_parsing(self, compounds):
        lis = []
        z = 0
        dump = ''
        for i in compounds:

            if 'Comp' in i:
                z = 1
                dump = ''
            if z == 0:
                lis.append(i)
            if ']' in i:
                z = 0
                dump += f'{i}'
                lis.append(dump)
            if z == 1:
                dump += f'{i}'

        return lis

    def concentrations_parsing(self, concentrations):
        regex = r'{([.\d\s]*)}'
        _concentrations = re.search(regex, concentrations[0])
        if _concentrations:
            _concentrations = _concentrations.group(1)

        concentrations = [0] * len(_concentrations.split())

        for i in range(len(_concentrations.split())):
            if float(_concentrations.split()[i]) or int(
                (_concentrations.split()[i])):
                concentrations[i] = Decimal(_concentrations.split()[i])
        return concentrations

    def template_process(self):
        head, compounds, concentrations = self.read_template()
        compounds = self.template_parsing(compounds)
        concentrations = self.concentrations_parsing(concentrations)
        return head, compounds, concentrations
    def generator(self, reaction: str, concentrations: list, n: str = None):
        if n:
            n = n
        else:
            n = '0.01'

        for i in range(len(concentrations)):
            for j in reaction.split():
                if int(j.split('=')[0]) == i:
                    concentrations[i] += Decimal(
                        (j.split('=')[1])) * Decimal(n)
        return concentrations

    def file_generator(self,
                       reaction: str,
                       n: str = None,
                       new_file: str = None,
                       t: str = '298.15'):
        head, compounds, concentrations = self.template_process()

        new_file = os.path.join(os.getcwd(), f'{new_file}.inp')

        with open(new_file, 'w') as f:
            for i in head:
                f.write(i)

            f.write(''.join(compounds))

            while all(True if i >= Decimal('0.0') else False
                      for i in concentrations):
                z = ' '.join([str(x) for x in concentrations])
                stt = 'henry  xh={'
                stt += z
                stt += '}  tk=%s GSOLV # Automatic Henry Law coefficient Calculation\n' % (
                    t)
                f.write(stt)
                concentrations = self.generator(concentrations=concentrations,
                                                reaction=reaction,
                                                n=n)

