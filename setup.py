from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = ''.join(f.readlines())

setup(
    name='spectra_downloader',
    version='0.1',
    description='Simple Python API for parsing SSAP query VOTABLEs and download spectra using '
                'direct method or DataLink protocol.',
    long_description=long_description,
    author='Jakub Koza',
    author_email='kozajaku@fit.cvut.cz',
    keywords='astronomy,SSAP,DataLink,spectra,spectrum',
    license='MIT',
    url='https://github.com/kozajaku/spectra-downloader',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=['requests'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'flexmock', 'betamax'],
)