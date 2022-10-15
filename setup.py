from setuptools import setup, find_packages

setup(
    name='FileArchiver',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['encode_terminal'],
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'encode = encode_terminal:encode',
            'decode = encode_terminal:decode'
        ],
    },
)