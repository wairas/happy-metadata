from setuptools import setup, find_namespace_packages


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="happy-metadata",
    description="Meta-data library for the Happy project for hyper-spectral data.",
    long_description=(
        _read('DESCRIPTION.rst') + b'\n' +
        _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/wairas/happy-metadata",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3',
    ],
    license='MIT License',
    install_requires=[
        "pandas",
        "simple-range>=0.0.2",
    ],
    package_dir={
        '': 'src'
    },
    packages=find_namespace_packages(where='src'),
    entry_points={
        "console_scripts": [
            "hmd-add-metadata=hmd.tools.add_metadata:sys_main",
        ]
    },
    version="0.0.1",
    author='Peter Reutemann',
    author_email='fracpete@waikato.ac.nz',
)
