import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="napkin",
    version="0.1.0",
    author="Hans Jang",
    author_email="hsjang8848@gmail.com",
    description="Python DSL for PlantUML sequence diagram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pinetr2e/napkin",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'napkin = napkin.cli:main',
        ],
    },
)
