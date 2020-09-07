## CosmOrc

Tools for automated screening of chemical space for screening and optimization of catalytic reactions in the liquid phase.

## Requirements and Installation

Requirements:

```
python>=3.6
Click==7.0
numpy==1.16.2
pandas==0.24.2
pyaml==19.4.1
python-dateutil==2.8.0
pytz==2019.3
PyYAML==5.1.2
six==1.12.0
typing==3.7.4.1
```

Simplest way to install CosmOrc:

```bash
    git clone https://github.com/akvatol/CosmOrc
```

```bash
    cd /CosmOrc
```

For pip, use:
```shell
    pip install -r requirements.txt
    pip install -e ../CosmOrc
```


To remove a package use:

```shell
    pip uninstall CosmOrc
```

Linux/Windows: Unfortunately, at the moment the package has not been tested for Windows usage.

## Simple examples

### Parsing

Команда принимает на вход один параметр, отвечающий за выбор парсера и неограниченное число аргументов: файлов для парсинга. 

```bash
	CosmOrc parsing -i orca /path/to/folder/*.out 
```

Данная команда аналогична использованию циклов в баше, like this:

```bash
	for f in *.log; do CosmOrc parsing $i -i orca; done
```

В случе исполнения для каждого *.out файла в дериктории будет создан файл *.csv с таким же именем, содержащий в себе основные термодинамические параметры молекулы.

На данный момент доступно три опции -i: cosmo, orca, gaussian, в качестве дефолтной выбран gaussian. 

**Обратите внимание** параметр cosmo, отвечает за парсинг *.tab файлов расчетов энергии сольватации программы cosmotherm. При использовании этой опции на каждый входной файл создается два файла *.csv. Содержащий непосредственно данные расчета сольватации **'Gsolv' - в Kcal/mol**, ln(gamma) и внутренний номер вещества в расчете CosmoTherm.

### Reaction

This is a simple example of input *.yaml file. **Pay attention to the number of indents.**

```yaml
Compounds:
- name: 'A'
  path_to_file: '/some/path/1.log'
  atom: True
- name: 'A2'
  path_to_file: '/some/path/2.log'
  linear: True
- name: 'A3'
  path_to_file: '/some/path/2.log'
  linear: False
Reactions:
- name: dimerization
  reaction: 2*A = A2
  condition:
    pressure: 1 1 1
    temperature: 250 350 5
- name: Trimerization
  reaction: 3*A = A3
  cosmo: /path/to/your.tab
```

Вместо ключа condition, можно использовать ключ cosmo - путь к *.tab файлу. Обратите внимание, что парсер tab файлов не меняет единицы измерения $G_{solv}$, однако класс Reaction_COSMO считает что на вход подаются Kcal/mol, будтье осторожны на счет этого.

#### Generator

Для облегчение расчета реакций предусмотрена команда generator, она рекурсивно ищет аут файлы  указанной программы, и генерирует Compounds часть yaml файла, в качестве имени файла используется название файла. Обратите внимание при использовании опции cosmo имя вещества должно **полностью совпадать** с именем указанным в tab файле.

```bash
	CosmOrc generator -p gaussian -i .log /path/to/folder
```









