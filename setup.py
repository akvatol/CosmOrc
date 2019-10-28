from setuptools import setup, find_packages

setup(
    name='CosmOrc',
    version='0.1',
    include_package_data=True,
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'pandas==0.24.2',
        'numpy==1.16.2',
        'Click==7.0',
        'typing==3.7.4.1',
    ],
    entry_points='''
        [console_scripts]
        CosmOrc = main:cli
    ''',
)
