from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shadowstep",
    version="1.0.1",
    author="Salih Sefer",
    author_email="sefersalih017@gmail.com",
    description="Advanced Anti-Forensics & System Artifact Management Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/s4l1hs/ShadowStep",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Environment :: Console",
    ],
    python_requires='>=3.6',
    install_requires=[
        "pyyaml",
        "colorama",
        "setproctitle",
        "psutil",
        "pywin32; sys_platform == 'win32'"
    ],
    entry_points={
        'console_scripts': [
            'shadowstep=shadowstep.cli:main', 
        ],
    },
)