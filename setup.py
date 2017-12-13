import setuptools

setuptools.setup(
    name="kallysto",
    version="0.1.0",
    url="tbd",

    author="Barry Smyth",
    author_email="barry.smyth@ucd.ie",

    description="Export Python data to Latex publications.",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
