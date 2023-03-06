import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qualitative-coding",
    version="0.2.2",
    author="Chris Proctor",
    author_email="pypi.org@accounts.chrisproctor.net",
    description="Qualitative coding tools for computer scientists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cproctor/qualitative-coding",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "PyYAML",
        "tabulate",
        "numpy",
    ],
    scripts=["qc"],
    python_requires='>=3.6',
)
