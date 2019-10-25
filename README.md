## CosmOrc

Tools for automated screening of chemical space for screening and optimization of catalytic reactions in the liquid phase.

## Requirements and Installation

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
    python3 setup.py install
```
To remove a package use:
```shell
    python3 setup.py --unistal
```

## Simple example

To provide some real life example: here is a simple CosmOrc usage examples:

```bash
	for i in *.log; do CosmOrc parsing $i -i g; done
```

Give you thermochemistry data for all *.log files in folder in *.csv format.

This is a simple example of input .yaml file. **Pay attention to the number of indents.**

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
  reaction: 2*A = A
  condition:
    pressure: 1 2 0.1
    temperature: 250 350 5
- name: Trimerization
  reaction: 2*A = A3
  condition:
    pressure: 1 2 0.1
    temperature: 250 350 5
```



## Quantum chemistry algorithm explaining

### Thermochemistry

На основании расчета частот колебаний, данная программа может перерасчитывать термодинамические параметры молекулы для заданого диапазона условий.  Вычисления выполняются по следующим формулам:
$$
G(T) = H(T) - T * S(T)
$$


#### Enthropy

Общаяя формула для вычисление энтропии:
$$
S(T) = S_{trans} + S_{rot} + S_{vib} + S_{el}
$$





$$
S_{trans} = n*R * ln(\frac{(2\pi MkT)^{3/2}V}{h^3N_A}) + \frac{5}{2}R \thickapprox n*R*(1.5*ln(M) + 2.5*ln(T) - ln(P) - 9.96)
$$





$$
S_{rot} = 
\begin{cases} 
   nR(ln(q_{rot}) + 1) &\text{for linear molecules}\\
   nR(ln(q_{rot}) + 1.5) &\text{for nonlinear molecules}
\end{cases}
$$
Where $ q_r  $ the rotational partition function:
$$
q_{rot} = 
\begin{cases} 
   \dfrac{1}{\sigma_{rot}}*(\dfrac{T}{\Theta_{rot}}) &\text{for linear molecules}\\
   \\
   \dfrac{\pi^{1/2}}{\sigma_{rot}}\bigg(\dfrac{T^{3/2}}{(\Theta_{rot, x}*\Theta_{rot, y}*\Theta_{rot, z})^{1/2}}\bigg) &\text{for nonlinear molecules}
\end{cases}
$$
In this program we take $ q_{rot} $  and $ \sigma_{rot}$ values from quantum output file. For Orca you can choose $\sigma_{rot}$ value.
$$
S_{vib} = n*R \sum_{\alpha}^{3N-6} \Biggl\{ \frac{U_{\alpha}}{exp(U_{\alpha}) - 1} - ln\big(1 - exp(-U_{\alpha})\big)\Biggl\}
$$
Where $ U_{\alpha}$ :
$$
U_{\alpha} = \frac{hv_\alpha}{kT}
$$

$$
S_{el} = nRln(W_{el})
$$



#### Entalpy

$$
H(T) = H_{trans} + H_{rot} + H_{vib} + E_0 + RT
$$

$$
H_{trans} =\frac{3}{2}RT
$$

$$
H_{rot} =
\begin{cases}
    nRT &\text{for linear molecules}\\
   \dfrac{3}{2}nRT &\text{for nonlinear molecules}
\end{cases}
$$

$$
H_{vib} = nR\sum_a^{3N-6}\dfrac{hv_\alpha}{exp(U_\alpha) - 1}
$$



$ n $ - число молей вещества, $ R $ - универсальная газовая постоянная, $ N_0 $ - число Авогадро, $M$ - Масса молекулы, $k$ - константа Больцмана, $T$ - температура, $p$ - давление, $h$ - постонянная Планка, $\sigma$ - число симметрии,  $v_\alpha$ - частота колебания, $W_{el}$ - кратность вырождения основного электронного состояния молекулы, $E_0$ - электронная энергия.



### COSMO-RS Theory 

https://pubs.acs.org/doi/pdf/10.1021/je025626e



### CosmOrc Algorithm explaining 

На первом шагу необходимо сделать парсинг  *.out файлов и убедится в корректности полученных данных. Иногда парсер не верно определяет  линейность молекулы, линейность **трехатомных молекул не всегда работает корректно.**  

- Оптимизация геометрии в квх программе
- Расчет COSMOфайла в турбомоль
- Расчет поправок COSMO-RS в CosmoTherm
- Создание входного файла и расчет реакции 

<img src="/home/anton/Documents/Scamt_projects/CosmOrc_public/image3_new.png" style="zoom:50%;" />



<center>
    <img src="/home/anton/Documents/Scamt_projects/CosmOrc_public/image7.png" alt="image7" style="zoom: 33%;" />
</center>
<justify> CosmOrc software algorithm diagram, *.out files of quantum chemical programs (Gaussian, Orca, COSMOTherm), or *.yaml files can be used as input. This input is used to create CosmOrc Compound objects. These objects are used as a repository of thermodynamic data. They help to create Reaction objects and recalculate thermodynamic data. These objects can be represented as text files of the specified format (* .txt, * .csv) for further processing and visualization. </justify>











