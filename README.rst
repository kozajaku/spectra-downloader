Spectra downloader
==================

Welcome to the documentation of Spectra downloader module. This is a simple Python3 tool that is capable of parsing
outputs of astronomical SSAP protocol and download selected spectra using a simple API. The tool supports both blocking
and non-blocking downloading methods and spectra listed in SSAP VOTABLES can be downloaded either by using direct
ACC_REF access or by using DataLink protocol with additional download parameters.

Documentation
-------------

Documentation can be found online on `spectra-downloader.readthedocs.io <http://spectra-downloader.readthedocs.io/>`_ or
you can build it manually by clonning the repository and executing::

    cd docs
    python3 -m pip install -r requirements.txt
    make html

Documentation is now created in ``docs/_build/html/``