from setuptools import setup, find_packages

setup(
    name='CosmOrc',
    version='0.1',
    include_package_data=True,
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'Click==7.0',
        'numpy==1.16.2',
        'pandas==0.24.2',
        'pyaml==19.4.1',
        'PySnooper==0.2.8',
        'python-dateutil==2.8.0',
        'pytz==2019.3',
        'PyYAML==5.1.2',
        'six==1.12.0',
        'typing==3.7.4.1',
    ],
    entry_points='''
        [console_scripts]
        CosmOrc = main:cli
    ''',
)
