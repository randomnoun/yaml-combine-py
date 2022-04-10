"""A package for combining yaml files.

See:
https://randomnoun.github.io/swagger-combine-maven-plugin/
https://github.com/randomnoun/swagger-combine-maven-plugin
"""

from setuptools import setup, find_namespace_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="yaml-combine",
    version="0.1.0",
    description="A YAML pre-processor to combine one or more YAML files with $xref references.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/randomnoun/yaml-combine-py",
    author="Greg Knox",
    author_email="knoxg@randomnoun.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="yaml, combine",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    namespace_packages=["randomnoun"],
    python_requires=">=3.6, <4",
    install_requires=["pyyaml"],
    extras_require={  # Optional
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    entry_points={
        "console_scripts": [
            "yaml-combine=randomnoun.yaml_combine.__main__:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/randomnoun/yaml-combine-py/issues",
        "Source": "https://github.com/randomnoun/yaml-combine-py/",
    },
)
