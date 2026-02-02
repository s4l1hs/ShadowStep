from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as req:
        return req.read().splitlines()

setup(
    name='shadowstep',
    version='1.0.0',
    description='Advanced System Artifact Management & Privacy Suite',
    author='Salih Sefer',
    packages=find_packages(),
    include_package_data=True,  # Required to include MANIFEST.in data
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'shadowstep=shadowstep:main',  # Run with 'shadowstep' in the terminal
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)