from setuptools import setup, find_packages

setup(
    name="structure",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "server = structure.cli:main",
        ]
    },
    install_requires=[
        # Add your package dependencies here, e.g. 'requests'
    ],
    author="Matthieu Moullec",
    author_email="matthieu@structure.tech",
    description="An LLM powered data structuring tool.",
    url="https://github.com/matthieu-perso/structure",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
