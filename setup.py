import setuptools
import re

with open('README.md', 'rt') as f:
    long_description = f.read()

with open('napkin/__init__.py', "rt") as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setuptools.setup(
    name='napkin',
    version=version,
    author='Hans Jang',
    author_email='hsjang8848@gmail.com',
    description='Python DSL for writing PlantUML sequence diagram',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pinetr2e/napkin',
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: Software Development',
    ],
    entry_points={
        'console_scripts': [
            'napkin = napkin.cli:main',
            'napkin_plantuml = napkin.plantuml_cli:main',
        ],
    },
)
