from setuptools import setup, find_packages

setup(
    name='CosmOrc',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'PySnooper==0.2.8',
        'pandas==0.24.2',
        'numpy==1.16.2',
        'Click==7.0',
        'typing==3.7.4.1',
    ],
    entry_points='''
        [console_scripts]
        main=CosmOrc:cli
    ''',
)